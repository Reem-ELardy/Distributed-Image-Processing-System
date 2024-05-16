import queue
import boto3
import cv2
import numpy as np
from mpi4py import MPI
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
print(rank)
processed_queue = queue.Queue()

s3 = boto3.client('s3')
bucket_name = 'imagesdis'

def upload_to_s3(image, bucket_name, key):
    _, encoded_image = cv2.imencode('.jpg', image)
    s3.put_object(Bucket=bucket_name, Key=key, Body=encoded_image.tobytes())

def download_from_s3(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_bytes = response['Body'].read()
    image_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)

def delete_image_from_s3(bucket_name, key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"Image '{key}' deleted from S3 bucket '{bucket_name}' successfully")
    except Exception as e:
        print("Error occurred while deleting image:", e)

def process_image(image, operation):
    if operation == 'edge_detection':
        return cv2.Canny(image, 70, 135)
    elif operation == 'color_manipulation':
        return cv2.bitwise_not(image)
    elif operation == 'blurring':
        return cv2.GaussianBlur(image, (5, 5), 0)
    else:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/processed', methods=['GET'])
def processed():
    try:
        if not processed_queue.empty():
            print("I am getting data")
            data = processed_queue.get(timeout=10)
            print(type(data))# Wait up to 10 seconds
            processed_image_path, image_id = data
            if processed_image_path is None:
                print("Big Big problem")

            print("Sending")
            response_data = {
                "processed_image": processed_image_path,
                "image_id": image_id
            }
            return jsonify(response_data), 200
        print("I am empty")
    except queue.Empty:
        return jsonify({"error": "No processed image available"}), 404


@app.route('/process', methods=['POST'])
def main():
    print(f"Main rank is: {rank}")
    if rank == 0:  # Master process
        # Extract the image data from the request payload
        data = request.json
        print("Received request from user app:", request.json)
        image_part = data.get('image_part')
        operation = data.get('operation')
        image_id = data.get('image_id')

        image = download_from_s3(bucket_name, image_part)

        if image is None:
            return jsonify({"error": "Failed to decode image data"}), 400
        print("Image is received")

        print("Start Splitting")
        # Splitting
        print(size)
        chunk_size = len(image) // (size - 1)  # Calculate the chunk size
        chunks = [image[i:i + chunk_size] for i in range(0, len(image), chunk_size)]

        for i in range(1, size):
            print("Sneding")
            comm.send((chunks[i - 1], operation), dest=i, tag=1)
            print("After sending", i)

        print("Sending is finished")

        # Receiving
        processed_chunks = []
        for i in range(1, size):
            print("Receive1")
            processed_chunk = comm.recv(source=i, tag=2)
            processed_chunks.append(processed_chunk)
            print("Receive2")

        print("Start concatenating")
        # Merge processed chunks into the final processed image
        processed_image = np.concatenate(processed_chunks)
        delete_image_from_s3(bucket_name, image_part)
        image_path = f"result{image_id}.jpg"
        upload_to_s3(processed_image, bucket_name, image_path)
        data = (image_path, image_id)
        print("Put in the queue")
        processed_queue.put(data)

        return jsonify({"message": "Image part received successfully."}), 200
    else:  # Worker processes
        while True:
            print(f"Worker rank is: {rank}")
            task = comm.recv(source=0, tag=1)
            print("Receiving")
            if task is None:
                print("task is empty")
                break
            print("Start operating")
            chunk, operation = task
            processed_chunk = process_image(chunk, operation)
            comm.send(processed_chunk, dest=0, tag=2)


if __name__ == "__main__":
    if rank == 0:
        app.run(host='0.0.0.0', port=8080)
    else:
        main()
    #
    # # Start Flask web server in a separate thread
    # flask_thread = threading.Thread(target=run_flask_app)
    # flask_thread.start()
    #
    # # Ensure that the worker processes exit cleanly
    # for i in range(1, size):
    #     comm.send(None, dest=i, tag=1)
    #
    # # Wait for the Flask thread to finish
    # flask_thread.join()

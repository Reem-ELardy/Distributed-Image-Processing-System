import queue

import cv2
import boto3
import numpy as np
import zmq
from mpi4py import MPI
import sys

# Initialize Boto3 S3 client
s3 = boto3.client('s3')
bucket_name = 'imagesdis'

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


# Upload processed image to S3
def upload_to_s3(image, bucket_name, key):
    _, encoded_image = cv2.imencode('.jpg', image)
    s3.put_object(Bucket=bucket_name, Key=key, Body=encoded_image.tobytes())


# Download image from S3
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


# Process image
def process_image(image, operation):
    if operation == 'edge_detection':
        return cv2.Canny(image, 70, 135)
    elif operation == 'color_manipulation':
        return cv2.bitwise_not(image)
    elif operation == 'blurring':
        return cv2.GaussianBlur(image, (5,5), 0)
    else:
        return None


# Main function for image processing
def image_processing_worker(image_path, operation):
    image = download_from_s3(bucket_name, image_path)
    if image is not None:
        processed_image = process_image(image, operation)
        if processed_image is not None:
            key = 'processed_image.jpg'
            upload_to_s3(processed_image, bucket_name, key)
            return key
    return None


if __name__ == "__main__":
    if rank == 0:  # Master process
        # Setup ZeroMQ context and sockets
        context = zmq.Context()
        user_socket = context.socket(zmq.REP)
        user_socket.bind("tcp://0.0.0.0:12345")

        while True:
            request = user_socket.recv_json()
            print("Received request from user app:", request)
            image_path = request.get("image")
            operation = request.get("operation")

            # Download the image
            image = download_from_s3(bucket_name, image_path)
            if image is None:
                print(f"Failed to download image '{image_path}' from S3.")
                continue

            # Spliting
            chunk_size = len(image) // (size - 1)  # Calculate the chunk size
            chunks = [image[i:i + chunk_size] for i in range(0, len(image), chunk_size)]
            for i in range(1, size):
                comm.send((chunks[i - 1], operation), dest=i, tag=1)

            # Receiving
            processed_chunks = []
            for i in range(1, size):
                processed_chunk = comm.recv(source=i, tag=2)
                processed_chunks.append(processed_chunk)

            # Merge processed chunks into the final processed image
            processed_image = np.concatenate(processed_chunks)

            delete_image_from_s3(bucket_name, image_path)

            # Upload the processed image to S3
            key = 'processed_image.jpg'
            upload_to_s3(processed_image, bucket_name, key)
            print(f"Processed image uploaded to S3 bucket '{bucket_name}' with key '{key}'")
            response_data = {"image": "processed_image.jpg"}
            user_socket.send_json(response_data)
            complete = input("Do you want to process any other images? (Y or N): ")
            if complete.upper() == 'N':
                user_socket.close()
                print("User Socket Closed")
                sys.exit()

    else:  # Worker processes
        while True:
            task = comm.recv(source=0, tag=1)
            if task is None:
                break
            chunk, operation = task
            processed_chunk = process_image(chunk, operation)
            comm.send(processed_chunk, dest=0, tag=2)
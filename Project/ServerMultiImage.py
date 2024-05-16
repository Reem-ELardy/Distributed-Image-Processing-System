import cv2
import boto3
import numpy as np
import zmq
import requests
import sys
import Script as run

size = 2

# Initialize Boto3 S3 client
s3 = boto3.client('s3')
bucket_name = 'imagesdis'

alb_endpoint1 = "http://distributed-alb-1595764367.eu-west-2.elb.amazonaws.com/process"
alb_endpoint2 = "http://distributed-alb-1595764367.eu-west-2.elb.amazonaws.com/processed"

pathes_to_send_to_user = []
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


# Function to send image parts to ALB
def send_image_parts_to_alb(image_part, operation, image_id):
    payload = {"image_part": image_part, "operation": operation, "image_id": image_id}
    response = requests.post(alb_endpoint1, json=payload)
    if response.status_code != 200:
        print(f"Failed to send image part {image_id}: {response.text}")


# Function to receive processed image parts from ALB
def receive_processed_image_parts_from_alb():
    response = requests.get(alb_endpoint2)
    if response.status_code == 200:
        response_data = response.json()
        processed_part_path = response_data["processed_image"]
        image_id = response_data["image_id"]
        return processed_part_path, image_id
    else:
        print("Failed to receive processed image parts from ALB.")
        return None, None


if __name__ == "__main__":
    context = zmq.Context()
    user_socket = context.socket(zmq.REP)
    user_socket.bind("tcp://0.0.0.0:12345")
    instance_id_used = []

    while True:
        request = user_socket.recv_json()
        print("Received request from user app:", request)
        image_paths_received_from_user = request.get("image")
        operation = request.get("operation")

        if len(image_paths_received_from_user) > 1:
            # if len(image_paths_received_from_user) > 4:
            #     instance_id_used = run.main1(4, run.region_name)
            # else:
            #     instance_id_used = run.main1(len(image_paths_received_from_user), run.region_name)

            image_id = 0
            for i in range(0, len(image_paths_received_from_user)):
                send_image_parts_to_alb(image_paths_received_from_user[i], operation, image_id)
                image_id = image_id + 1
            print("All image parts sent successfully.")

            resulted_image = {}
            for _ in range(len(image_paths_received_from_user)):
                print("Receiving")
                process_image_path, image_id = receive_processed_image_parts_from_alb()
                print("Received image number ", image_id)
                if process_image_path is not None:
                    resulted_image[image_id] = process_image_path

            print("All processed image parts received.")
            sorted_dict = dict(sorted(resulted_image.items()))
            print(type(sorted_dict))

            processed_image = list(sorted_dict.values())

            #run.main2(instance_id_used, run.region_name)

            pathes_to_send_to_user = processed_image
            for path in image_paths_received_from_user:
                delete_image_from_s3(bucket_name, path)

            response_data = {"image": pathes_to_send_to_user}
            user_socket.send_json(response_data)

        else:
            # Download the image
            image = download_from_s3(bucket_name, image_paths_received_from_user[0])
            if image is None:
                print(f"Failed to download image '{image_paths_received_from_user[0]}' from S3.")
                continue

            #instance_id_used = run.main1(2, run.region_name)

            # Splitting the image into parts
            chunk_size = len(image) // size  # Calculate the chunk size
            chunks = [image[i:i + chunk_size] for i in range(0, len(image), chunk_size)]
            print("split is done")

            image_id = 0
            for i in range(0, size):
                print(f"Sending part{image_id}")
                image_path = f"part{image_id}.jpg"
                upload_to_s3(chunks[i], bucket_name, image_path)
                send_image_parts_to_alb(image_path, operation, image_id)
                image_id = image_id +1
            print("All image parts sent successfully.")

            # Receiving processed image parts
            processed_chunks = {}
            for _ in range(size):
                print("Receiving")
                processed_chunk, image_id = receive_processed_image_parts_from_alb()
                print("Received image number ", image_id)
                if processed_chunk is not None:
                    image = download_from_s3(bucket_name, processed_chunk)
                    processed_chunks[image_id] = image
                    delete_image_from_s3(bucket_name, processed_chunk)

            print("All processed image parts received.")
            sorted_dict = dict(sorted(processed_chunks.items()))
            print(type(sorted_dict))

            processed_chunks = list(sorted_dict.values())

            #run.main2(instance_id_used, run.region_name)

            # Merge processed chunks into the final processed image
            processed_image = np.concatenate(processed_chunks)
            print("Image reassembly complete.")

            delete_image_from_s3(bucket_name, image_paths_received_from_user[0])

            # Upload the processed image to S3
            key = 'processed_image.jpg'
            upload_to_s3(processed_image, bucket_name, key)
            print(f"Processed image uploaded to S3 bucket '{bucket_name}' with key '{key}'")
            pathes_to_send_to_user.append(key)
            response_data = {"image": pathes_to_send_to_user}
            user_socket.send_json(response_data)

        complete = input("Do you want to process any other images? (Y or N): ")
        if complete.upper() == 'N':
            user_socket.close()
            print("User Socket Closed")
            sys.exit()
        else:
            print("Processing next image.")

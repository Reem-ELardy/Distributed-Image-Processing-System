import queue

import boto3
import cv2
import numpy as np
import zmq

# Initialize Boto3 S3 client
s3 = boto3.client('s3')

# Image details
bucket_name = 'imagesdis'  # Name of your S3 bucket
image_paths = []

image_paths_to_upload_to_s3 = []
image_paths_to_send_to_server = []
message_queue = queue.Queue()

# Function to download image from S3
def download_image_from_s3(bucket_name, object_key, local_path):
    try:
        s3.download_file(bucket_name, object_key, local_path)
    except Exception as e:
        print("Error downloading image from S3:", e)


# Function to upload image to S3
def upload_image_to_s3(image_path, bucket_name, object_key):
    try:
        s3.upload_file(image_path, bucket_name, object_key)
    except Exception as e:
        print("Error uploading image to S3:", e)

def progress():
    if message_queue.empty():
        return None
    Message = message_queue.get()
    return Message

# Function to delete image from S3
def delete_image_from_s3(bucket_name, key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"Image '{key}' deleted from S3 bucket '{bucket_name}' successfully")
    except Exception as e:
        print("Error occurred while deleting image:", e)


def get_from_s3(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_bytes = response['Body'].read()
    image_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


def main(image_paths_to_upload_to_s3, operation):
    # Setup ZeroMQ context and socket for user requests
    context = zmq.Context()
    request_socket = context.socket(zmq.REQ)
    request_socket.connect("tcp://18.171.159.6:12345")
    monitor_socket = context.socket(zmq.PULL)
    monitor_socket.connect("tcp://18.171.159.6:12346")
    print("Connection is done")

    image_num = 0
    for path in image_paths_to_upload_to_s3:
        object_key = f'Original_Image{image_num}.jpg'  # Key under which the image will be stored in S3

        # Upload image to S3
        upload_image_to_s3(path, bucket_name, object_key)
        print("Image uploaded")
        image_paths_to_send_to_server.append(object_key)
        image_num += 1

    # Send request to the server
    request_data = {"image": image_paths_to_send_to_server, "operation": operation}
    request_socket.send_json(request_data)
    print("Sent request:", request_data)

    print("Monitoring messages Start")
    while True:
        response = monitor_socket.recv_json()
        if 'message' in response:
            Message = response['message']
            message_queue.put(Message)
            if Message == "Sending back to user":
                break

    # Receive response from the server
    response = request_socket.recv_json()

    image_paths_to_receive_from_server = response['image']

    return image_paths_to_receive_from_server


def download(image_paths_to_receive_from_server):
    if len(image_paths_to_receive_from_server) > 1:
        image_num = 0
        for path in image_paths_to_receive_from_server:
            # Download processed image from S3
            processed_image_local_path = f"C://Mine//Pycharm//Distributed//Resulted_images//resulted_image{image_num}.jpg"
            download_image_from_s3(bucket_name, image_paths_to_receive_from_server[image_num], processed_image_local_path)

            # Delete processed image from S3
            delete_image_from_s3(bucket_name, image_paths_to_receive_from_server[image_num])
            image_num += 1
    else:
        processed_image_local_path = 'C://Mine//Pycharm//Distributed//Resulted_images//resulted_image.jpg'
        download_image_from_s3(bucket_name, image_paths_to_receive_from_server[0], processed_image_local_path)

        # Delete processed image from S3
        delete_image_from_s3(bucket_name, image_paths_to_receive_from_server[0])
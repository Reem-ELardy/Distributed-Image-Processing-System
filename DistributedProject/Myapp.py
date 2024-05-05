import time
import cv2
import numpy as np
import boto3
import zmq

# Initialize Boto3 S3 client
s3 = boto3.client('s3')

# Image details
bucket_name = 'imagesdis'  # Name of your S3 bucket
object_key = 'Original_Image.jpg'  # Key under which the image will be stored in S3
image_path = 'images3.jpg'
operation = 'edge_detection'

# Function to download image from S3
def download_image_from_s3(bucket_name, object_key, local_path):
    try:
        s3.download_file(bucket_name, object_key, local_path)
    except Exception as e:
        print("Error downloading image from S3:", e)
        download_image_from_s3(bucket_name, object_key, processed_image_local_path)


# Function to upload image to S3
def upload_image_to_s3(image_path, bucket_name, object_key):
    try:
        s3.upload_file(image_path, bucket_name, object_key)
    except Exception as e:
        print("Error uploading image to S3:", e)
        upload_image_to_s3(image_path, bucket_name, object_key)


# Function to delete image from S3
def delete_image_from_s3(bucket_name, key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"Image '{key}' deleted from S3 bucket '{bucket_name}' successfully")
    except Exception as e:
        print("Error occurred while deleting image:", e)
        delete_image_from_s3(bucket_name, key)


if __name__ == "__main__":
    # Setup ZeroMQ context and socket for user requests
    context = zmq.Context()
    request_socket = context.socket(zmq.REQ)
    request_socket.connect("tcp://35.179.96.48:12345")


    # Upload image to S3
    upload_image_to_s3(image_path, bucket_name, object_key)
    print("Image uploaded")

    # Send request to the server
    request_data = {"image": "Original_Image.jpg", "operation": operation}
    request_socket.send_json(request_data)
    print("Sent request:", request_data)

    # Receive response from the server
    response = request_socket.recv_json()
    print("Received response:", response)

    # Download processed image from S3
    processed_image_local_path = 'resulted_image3.jpg'
    download_image_from_s3(bucket_name, response['image'], processed_image_local_path)

    # Delete processed image from S3
    delete_image_from_s3(bucket_name, response['image'])

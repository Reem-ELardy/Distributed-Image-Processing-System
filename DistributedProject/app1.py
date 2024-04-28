import time

import cv2
import boto3
import numpy as np
from mpi4py import MPI
import threading
import queue
import sys
#from ImageProcessingAlgo import *

# Initialize Boto3 S3 client
s3 = boto3.client('s3')
bucket_name = 'imagesdis'
object_key = 'uploaded_image.jpg'  # The object key of the uploaded image in the S3 bucket

kernal=(5,5)
sigma=0


#image edge detection
def Image_Edge_Detection(image):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    Processed_image = cv2.Canny(gray_image, 70, 135)

    return Processed_image

#image color mianpulation
def Image_Color_Mainpulation(image):

    processed_Image = cv2.bitwise_not(image)

    return processed_Image

#image blurred
def Image_blurring(image):

    processed_Image = cv2.GaussianBlur(image, kernal, sigma)

    return processed_Image

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

def accessing_from_s3(bucket_name, key):
    response = s3.head_object(Bucket=bucket_name, Key=key)
    return response

def delete_image_from_s3(bucket_name, key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"Image '{key}' deleted from S3 bucket '{bucket_name}' successfully")
    except Exception as e:
        print("Error occurred while deleting image:", e)

#image processing function
def process_image(image, operation):
    if operation == 'edge_detection':
        return Image_Edge_Detection(image)
    elif operation == 'color_manipulation':
        return Image_Color_Mainpulation(image)
    elif operation == 'blurring':
        return Image_blurring(image)
    else:
        return None

# Main function for image processing
def image_processing_worker(task_queue):
    while True:
        task = task_queue.get()
        if task is None:
            break
        image, operation = task
        # Read the image
        if image is None:
            print(f"Failed to read image from file: dvhdv")
        else:
            # Perform image processing
            processed_image = process_image(image, operation)
            delete_image_from_s3(bucket_name, object_key)
            if processed_image is not None:
                # Upload processed image to S3
                key = 'processed_image.jpg'  # Modify key to avoid conflicts
                upload_to_s3(processed_image, bucket_name, key)
                print(f"Processed image uploaded to S3 bucket '{bucket_name}' with key '{key}'")

        if task_queue.empty():
            break


# Main function
if __name__ == "__main__":
    task_queue = queue.Queue()
    while True:
        while True:
            try:
                response = accessing_from_s3(bucket_name, object_key)
                # If the object exists, break the loop
                if response:
                    print("Processed image found on S3!")
                    break
            except Exception as e:
                print()
            # Wait for 5 seconds before checking again
            time.sleep(10)

        image = download_from_s3(bucket_name, object_key)

        operation = input("Please choose one of the operations:\n"
                          "1. edge_detection\n"
                          "2. color_manipulation\n"
                          "3. blurring\n"
                          "Your choice: ")

        # Add tasks to the queue
        tasks = [(image, operation)]
        for task in tasks:
            task_queue.put(task)

        # Distribute tasks among EC2 instances using MPI
        image_processing_worker(task_queue)
        complete = input("do you want to procross any other images Y or N?")
        if complete == 'N':
            sys.exit()
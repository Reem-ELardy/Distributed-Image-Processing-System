import time
import cv2
import numpy as np
import requests
import boto3

s3 = boto3.client('s3')

def download_image_from_s3(bucket_name, object_key, local_path):
    # Download image from S3
    s3.download_file(bucket_name, object_key, local_path)

def upload_image_to_s3(image_path, bucket_name, object_key):
    # Upload image to S3
    s3.upload_file(image_path, bucket_name, object_key)

def accessing_from_s3(bucket_name, key):
    response = s3.head_object(Bucket=bucket_name, Key=key)
    return response

def acessing_from_s3(bucket_name, key):
    s3.get_object(Bucket=bucket_name, Key=key)
    image_bytes = response['Body'].read()
    image_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)

def delete_image_from_s3(bucket_name, key):
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"Image '{key}' deleted from S3 bucket '{bucket_name}' successfully")
    except Exception as e:
        print("Error occurred while deleting image:", e)


if __name__ == "__main__":
    for i in {1, 2, 3}:
        # Image details
        image_path = f'images{i}.jpg'  # Local path of the image
        bucket_name = 'imagesdis'   # Name of your S3 bucket
        object_key = 'uploaded_image.jpg'  # Key under which the image will be stored in S3
        # operation = "edge_detection"  # Operation to perform on the image

        # Upload image to S3
        upload_image_to_s3(image_path, bucket_name, object_key)
        print("Image uploaded")
        # upload_image(object_key, operation)
        # Send object_key to EC2 instance for processing
        # result = upload_image(object_key, operation)


        # Once processing is done on EC2 instance, download the processed image from S3
        processed_image_key = 'processed_image.jpg'  # Key of the processed image in S3

        while True:
            try:
                response = accessing_from_s3(bucket_name, processed_image_key)
                # If the object exists, break the loop
                if response:
                    print("Processed image found on S3!")
                    break
            except Exception as e:
                pass
            # Wait for 5 seconds before checking again
            time.sleep(5)


        processed_image_local_path = f'resulted_image{i}.jpg'  # Local path to save the processed image
        download_image_from_s3(bucket_name, processed_image_key, processed_image_local_path)
        delete_image_from_s3(bucket_name, processed_image_key)
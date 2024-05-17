# Distributed Image Processing using Cloud Platforms 

A brief description of your project, what it does, and why it is useful.

## Table of Contents
- [Runing and Compile](#Runing-and-Compile)
- [EC2 set up and configuration for running Server-side ](#Ec2-set-up-and-configuration-for-running-Server---side )
- [Local set up and configuration for running Client-side ](#Local-set-up-and-configuration-for-running-Client---side )
- [Demo link](#Dome-link)
  
## Runing and Compile

Our application on two sides:
- Server-side: is running on a cloud platform which is AWS as we use EC2 instances as virtual machines to run the server code on it, these intances do different jobs as one of them are a Master EC2 that communicate with the Client-side directly and when it recieve from the Client-side an image for example, it spilit image and send to Alb to distribute on other EC2 instance while the others are called worker as they are responsible processing image parts then send it back to Master EC2 
- Client-side: is locally on laptop 

## EC2 set up and configuration

 1. Worker Instance Setup

Open a terminal on your EC2 Worker instance and run the following commands:

-Install `python3-pip`:
    ```bash
    sudo apt install python3-pip
    ```

- Update package lists:
    ```bash
    sudo apt update
    ```

- Install MPI and `mpi4py`:
    ```bash
    sudo apt install mpich
    sudo apt install python3-mpi4py
    ```

- Install Flask:
    ```bash
    pip install Flask
    ```

- Install OpenCV for Python:
    ```bash
    sudo apt install python3-opencv
    sudo apt update && sudo apt upgrade -y
    ```

- Install Boto3:
    ```bash
    sudo apt install python3-boto3
    ```

- Install pipx and configure the environment:
    ```bash
    sudo apt update
    sudo apt install pipx
    sudo apt install python3-pip
    sudo apt install python3-venv
    pipx ensurepath
    pipx install awscli
    export PATH="$PATH:/home/ubuntu/.local/bin"
    ```

    2. Server Instance Setup

Open a terminal on your EC2 Server instance and run the following commands:

- Install `python3-pip`:
    ```bash
    sudo apt install python3-pip
    ```

- Update package lists:
    ```bash
    sudo apt update
    ```

- Install MPI and `mpi4py`:
    ```bash
    sudo apt install mpich
    sudo apt install python3-mpi4py
    ```

- Install zmq:
    ```bash
    pip install zmq
    ```

- Install OpenCV for Python:
    ```bash
    sudo apt install python3-opencv
    sudo apt update && sudo apt upgrade -y
    ```

- Install Boto3:
    ```bash
    sudo apt install python3-boto3
    ```

- Install pipx and configure the environment:
    ```bash
    sudo apt update
    sudo apt install pipx
    sudo apt install python3-pip
    sudo apt install python3-venv
    pipx ensurepath
    pipx install awscli
    export PATH="$PATH:/home/ubuntu/.local/bin"
    ```

3. AWS CLI Configuration

After installing AWS CLI on both Worker and Server instances, configure it using the following commands:

```bash
aws --version
aws configure
```
**Note:** Ensure that you replace the AWS Access Key ID and Secret Access Key with your actual credentials. Keep your credentials secure and do not expose them publicly.
AWS Access Key ID [None]: AKIAZQ3DOOXZ232RYEVJ
AWS Secret Access Key [None]: aEAaa1dru3Bmbtpssjt2DvnpJzcwO95yU3nGFXgd
Default region name [None]: us-west-2
Default output format [None]: json

4. NIAM Role for Server Instances
Ensure that the Server instance has the correct IAM role attached with the necessary permissions to interact with other instances and the Application Load Balancer (ALB). The IAM role should include at least the AmazonEC2RoleforSSM managed policy. This can be done via the AWS Management Console or the AWS CLI.

## Local set up and configuration for running Client-side 

 Open you windows command line.
2. Install the required packages using pip:
    ```bash
    pip install tk
    pip install customtkinter
    pip install pillow
    pip install queue
    pip install boto3
    pip install opencv-python
    pip install numpy
    pip install zmq
    ```

**Note:** Make sure to replace `pip` with `pip3` if you're using Python 3.x.

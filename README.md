# Distributed Image Processing using Cloud Platforms 

A brief description of your project, what it does, and why it is useful.

## Table of Contents
- [Runing and Compile](#Runing-and-Compile)
- [EC2 set up and configuration](#Ec2-set-up-and-configuration)
- [Local set up and configuration](#Local-set-up-and-configuration)
- [Demo link](#Dome-link)
  
##Runing and Compile

Our application on two sides:
- Server-side: is running on a cloud platform which is AWS as we use EC2 instances as virtual machines to run the server code on it, these intances do different jobs as one of them are a Master EC2 that communicate with the Client-side directly and when it recieve from the Client-side an image for example, it spilit image and send to Alb to distribute on other EC2 instance while the others are called worker as they are responsible processing image parts then send it back to Master EC2 
- Client-side: is locally on laptop 

##EC2 set up and configuration

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

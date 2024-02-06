# Maintenance Server

Welcome to the Maintenance Server repository.

## Overview

Maintenance Server is a project created to handle the server side of other projects me and my friends are working on which are an [Android application](https://github.com/SUFIYANJT/application32) and a [Website](https://github.com/karthikeyan-ks/Maintenance-client/).

## Features

- **Django-Powered:** Built on the robust Django framework, Maintenance Server leverages the power and versatility of Django for seamless server-side operations.

## Getting Started

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/Maintenance-server.git
    cd Maintenance-server
    ```

2. **Install Dependencies:**
    ```bash
    
    
    sudo apt install python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config python3-pip gcc gdb
    
    
    ```

    **Note:** Maintenance Server was developed on Ubuntu as the operating system. Ensure you have Ubuntu or some other Linux Distributions installed before proceeding.

3. **Create python virtual environment , if necessary.**
    
    ```bash
    python3 -m venv $VENV_NAME
    ```
4. **Activate virtual environment**
    ```bash
    source $VENV_NAME/bin/activate
    ```
5. **Install Packages**
    ```bash
    pip install -r requirements.txt
    ```
6. **Run Django server**
    ```bash
    ./manage.py runserver
    ```
    
Read the wiki for instructions on how to setup **NGINX** server with **Daphne** ASGI server, Docker for **Redis** , and **MySQL**.

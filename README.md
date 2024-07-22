# File Manager on Docker

This repository contains a full-stack web application with separate backend and frontend components. The project demonstrates the use of Docker for containerizing the application and includes scripts and configurations for both services.

![image](https://github.com/user-attachments/assets/3875f5f9-2c04-407c-ab3d-dbcd6cd206f6)

## Project Overview

The project is structured into two main components:

1. **Backend**: A Python-based backend that interacts with an S3 storage and serves API requests.
2. **Frontend**: A web-based frontend built with HTML, CSS, and JavaScript.

## Repository Structure

- **docker-compose.yml**: The Docker Compose configuration file to orchestrate multi-container Docker applications.
- **backend/**: Contains all files related to the backend service.
  - `Dockerfile`: Defines the Docker image for the backend.
  - `requirements.txt`: Lists the Python dependencies for the backend service.
  - `s3_utils.py`: Utility functions for interacting with S3 storage.
  - `server.py`: The main Python script for running the backend server.
- **frontend/**: Contains all files related to the frontend service.
  - `Dockerfile`: Defines the Docker image for the frontend.
  - `index.html`: The HTML file for the frontend UI.
  - `script.js`: The JavaScript file for frontend logic.
  - `styles.css`: The CSS file for frontend styling.

## How the Project Works

### Backend

The backend service is built using Python and serves as an API to interact with the frontend and perform operations such as fetching or storing data. The `server.py` script is the entry point for the backend server, and it uses `s3_utils.py` for interactions with Amazon S3 storage.

1. **Dockerfile**:
   - This file specifies the base image, dependencies, and instructions for building the backend Docker image.

   ```dockerfile
   FROM python:3.8-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "server.py"]
   ```

2. **requirements.txt**:
   - Lists Python packages required for the backend. These packages are installed inside the Docker container.

   ```text
   flask
   boto3
   ```

3. **s3_utils.py**:
   - Contains functions to interact with AWS S3, such as uploading or downloading files.

4. **server.py**:
   - A Flask application that handles HTTP requests and interacts with the S3 service using `s3_utils.py`.

   ```python
   from flask import Flask, request
   import s3_utils

   app = Flask(__name__)

   @app.route('/upload', methods=['POST'])
   def upload():
       file = request.files['file']
       s3_utils.upload_to_s3(file)
       return "File uploaded successfully!"

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```

### Frontend

The frontend service is a simple web application that interacts with the backend API to display data and perform operations.

1. **Dockerfile**:
   - This file specifies the base image and instructions for building the frontend Docker image.

   ```dockerfile
   FROM nginx:alpine
   COPY . /usr/share/nginx/html
   ```

2. **index.html**:
   - The main HTML file that provides the structure of the web application.

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Frontend</title>
       <link rel="stylesheet" href="styles.css">
   </head>
   <body>
       <h1>Frontend Interface</h1>
       <input type="file" id="fileInput">
       <button id="uploadBtn">Upload</button>
       <script src="script.js"></script>
   </body>
   </html>
   ```

3. **script.js**:
   - JavaScript code that handles the frontend logic, such as sending file uploads to the backend API.

   ```javascript
   document.getElementById('uploadBtn').addEventListener('click', () => {
       const fileInput = document.getElementById('fileInput');
       const file = fileInput.files[0];

       const formData = new FormData();
       formData.append('file', file);

       fetch('/upload', {
           method: 'POST',
           body: formData
       })
       .then(response => response.text())
       .then(data => alert(data))
       .catch(error => console.error('Error:', error));
   });
   ```


## How to Run the Project

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.

### Running the Application


1. **Build and Start the Application**:
   ```bash
   docker-compose up --build
   ```

2. **Access the Application**:
   - Open a web browser and navigate to `http://localhost:5000` to access the frontend interface.
   - Use the interface to upload files, which will be processed by the backend.


## Notes

- Ensure your AWS credentials are properly configured for the backend to access S3 storage.
- Modify the configurations as necessary to suit your specific use case or environment.

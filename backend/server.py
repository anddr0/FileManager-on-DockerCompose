from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from s3_utils import create_bucket_if_not_exists, upload_file_to_s3, list_files_in_s3, generate_presigned_url, create_s3_client, rename_file_in_s3, BUCKET_NAME

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

create_bucket_if_not_exists(BUCKET_NAME)

def sync_db_with_s3():
    s3_files = list_files_in_s3(BUCKET_NAME)
    s3_files_dict = {file['name']: file['url'] for file in s3_files}

    # Fetch all files currently in the database
    db_files = File.query.all()
    db_files_dict = {file.name: file for file in db_files}

    # Add new files from S3 to the database
    for name, url in s3_files_dict.items():
        if name not in db_files_dict:
            presigned_url = generate_presigned_url(BUCKET_NAME, name)
            new_file = File(name=name, url=presigned_url)
            db.session.add(new_file)
        else:
            # Update the presigned URL for existing files
            db_file = db_files_dict[name]
            db_file.url = generate_presigned_url(BUCKET_NAME, name)

    # Remove files from the database that are no longer in S3
    for name in db_files_dict.keys():
        if name not in s3_files_dict:
            db.session.delete(db_files_dict[name])
    
    db.session.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    custom_name = request.form.get('customName')
    
    if custom_name:
        file_extension = file.filename.split('.')[-1]
        file_name = f"{custom_name}.{file_extension}"
    else:
        file_name = file.filename

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(file_path)

    s3_url = upload_file_to_s3(file_path, BUCKET_NAME, file_name)

    # Generate the presigned URL and store it in the database
    presigned_url = generate_presigned_url(BUCKET_NAME, file_name)
    new_file = File(name=file_name, url=presigned_url)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"id": new_file.id, "name": new_file.name, "url": new_file.url})

@app.route('/rename/<int:file_id>', methods=['PUT'])
def rename_file(file_id):
    new_name = request.form['name']
    file = File.query.get_or_404(file_id)
    file_extension = file.name.split('.')[-1]
    new_file_name = f"{new_name}.{file_extension}"

    # Rename the file in S3
    s3_url = rename_file_in_s3(BUCKET_NAME, file.name, new_file_name)

    # Update the database record and regenerate the presigned URL
    presigned_url = generate_presigned_url(BUCKET_NAME, new_file_name)
    file.name = new_file_name
    file.url = presigned_url
    db.session.commit()

    return jsonify({"id": file.id, "name": file.name, "url": file.url})

@app.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    # Deleting from S3
    s3_client = create_s3_client()
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=file.name)
    
    # Deleting from database
    db.session.delete(file)
    db.session.commit()

    return jsonify({"message": "File deleted"})

@app.route('/get_files', methods=['GET'])
def get_files():
    sync_db_with_s3()  # Sync the database with S3
    files = File.query.all()
    file_list = [{"id": file.id, "name": file.name, "url": file.url} for file in files]
    return jsonify(file_list)

@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    return jsonify({"url": file.url})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

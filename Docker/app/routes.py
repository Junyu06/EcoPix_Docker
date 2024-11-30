from flask import request, jsonify
from app import app, db
from app.models import Photo

@app.route("/photos", methods=["GET"])
def get_photos():
    photos = Photo.query.all()
    return jsonify([{"id": p.id, "filename": p.filename, "uploaded_at": p.uploaded_at} for p in photos])

@app.route("/upload", methods=["POST"])
def upload_photo():
    file = request.files["photo"]
    metadata = request.form.get("metadata")

    # Save file and metadata
    new_photo = Photo(filename=file.filename, metadata=metadata)
    db.session.add(new_photo)
    db.session.commit()
    
    return jsonify({"message": "Photo uploaded successfully!"})

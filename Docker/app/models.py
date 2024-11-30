from app import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())
    metadata = db.Column(db.JSON, nullable=True)

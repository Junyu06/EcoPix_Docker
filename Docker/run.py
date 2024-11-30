from flask import Flask
from app.route import routes  # Import the Blueprint

app = Flask(__name__)

# Register the Blueprint
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15381)

import datetime
from flask import Flask, jsonify, render_template, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
from models import db, User

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True 
app.config['ENV'] = "development" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['JWT_SECRET_KEY'] = "0682f007844a0266990df1b2912f95bc"

db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
CORS(app)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)


    if not username:
        return jsonify({"msg": "Username is required"}), 400

    if not password:
        return jsonify({"msg": "Password is required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "username/password are incorrect"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "username/password are incorrect"}), 401

    expires = datetime.timedelta(seconds=30) # Duracion para el token
    data = {
        "access_token": create_access_token(identity=user.username, expires_delta=expires),
        "user": user.serialize() 
    }

    return jsonify(data), 200

@app.route('/api/register', methods=['POST'])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    nombre = request.json.get("nombre", None)
    apellido = request.json.get("apellido", None)
    edad = request.json.get("edad", None)
    email = request.json.get("email", None)
    telefono = request.json.get("telefono", None)
    direccion = request.json.get("direccion", None)
    role_id = request.json.get("role_id", None)

    if not username:
        return jsonify({"msg": "Username is required"}), 400

    if not password:
        return jsonify({"msg": "Password is required"}), 400

    if not nombre:
        return jsonify({"msg": "Nombre is required"}), 400

    if not apellido:
        return jsonify({"msg": "Apellido is required"}), 400

    if not edad:
        return jsonify({"msg": "Edad is required"}), 400

    if not email:
        return jsonify({"msg": "Email is required"}), 400

    if not telefono:
        return jsonify({"msg": "Email is required"}), 400

    if not direccion:
        return jsonify({"msg": "Email is required"}), 400

    if not role_id:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({"msg": "Username already exists"}), 400

    user = User()
    user.username = username
    user.nombre = nombre
    user.apellido = apellido
    user.edad = edad
    user.email = email
    user.telefono = telefono
    user.direccion = direccion
    user.role_id = role_id
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "registro existo, por favor hacer login"}), 201


@app.route("/api/users", methods=['GET', 'POST'])
@jwt_required
def users():
    pass

@app.route('/api/profile')
@jwt_required
def profile():
    username = get_jwt_identity()
    user = User.query.filter_by( username=username ).first()
    return jsonify({"msg": f"Perfil del usuario {username}", "user": user.serialize()}), 200

if __name__ == "__main__":
    manager.run()
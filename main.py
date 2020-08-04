import datetime
from flask import Flask, jsonify, render_template, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
from models import db, User, Person, Address, Pregunta, Respuesta, Quiz

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
#       
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

# .......................... LOGIN ....................................... 
# _____________________________________________________________________________________________________________________________________________
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

# .......................... REGISTER ....................................... 
# _____________________________________________________________________________________________________________________________________________    
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

# .......................... USERS ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route("/api/users", methods=['GET', 'POST'])
@jwt_required
def users():
    pass
# .......................... PROFILE ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/profile')
@jwt_required
def profile():
    username = get_jwt_identity()
    user = User.query.filter_by( username=username ).first()
    return jsonify({"msg": f"Perfil del usuario {username}", "user": user.serialize()}), 200

# ..................... AGREGAR TITULO AL QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/add_titulo_quiz', methods=['POST'])
def add_titulo_quiz():
    titulo = request.json.get("titulo", None)

    if not titulo:
       return jsonify({"msg": "titulo is required"}), 400

    
    quiz = Quiz.query.filter_by(titulo=titulo).first()

    if quiz:
        return jsonify({"msg": "Titulo already exists"}), 400

    
    quiz = Quiz()
    quiz.titulo = titulo
    
    quiz.guardar()

    return jsonify(quiz.serialize()), 201

# .......................... REGRESAR EL TITULO DEL QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_quiz', methods=['GET'])
def recibir_quiz():
    quizs = Quiz.query.all() 
    quizs = list( map(lambda quiz: quiz.serialize(), quizs)) 
    return jsonify(quizs), 200

# .......................... REGRESAR EL TITULO DE UN QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_quiz/<int:id>', methods=['GET'])
def recibir_quiz_especifico(id):
    get = Quiz.query.filter_by( id=id ).first()
    if get:
        return jsonify({"msg": get.serialize()}), 200

# .................... AGREGAR PREGUNTAS AL QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/add_preguntas_quiz', methods=['POST'])
def add_preguntas_quiz():
    pregunta = request.json.get("pregunta", None)
    quiz_id = request.json.get("quiz_id", None)

    if not pregunta:
       return jsonify({"msg": "pregunta is required"}), 400

    if not quiz_id:
        return jsonify({"msg": "quiz_id is required"}), 400

    preguntas = Pregunta.query.filter_by(pregunta=pregunta).first()

    if preguntas:
        return jsonify({"msg": "Pregunta already exists"}), 400

    quiz_ids = Quiz.query.filter_by(id=quiz_id).first()

    if quiz_ids is None:
        return jsonify({"msg": "Quiz_id already not exists"}), 400

    preguntas = Pregunta()
    preguntas.pregunta = pregunta
    preguntas.quiz_id = quiz_id
    preguntas.guardar()
            
    return jsonify({"msg": "listo"}), 200
    
    
    """ return jsonify(preguntas.serialize()), 201"""
    
# .................... OBTENER PREGUNTAS DEL QUIZ  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_preguntas', methods=['GET'])
def get_preguntas():
    preguntas = Pregunta.query.all() 
    preguntas = list( map(lambda pregunta: pregunta.serialize(), preguntas)) 
    return jsonify(preguntas), 200

# .................... OBTENER PREGUNTA ESPECIFICA DEL QUIZ  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_preguntas/<int:id>', methods=['GET'])
def get_preguntas_pos(id):
    filtrado = Pregunta.query.filter_by(id=id).first()
    if filtrado:
        return jsonify({"msg": filtrado.serialize()}), 200


# ..................... AGREGAR RESPUESTAS AL QUIZ   ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/add_respuestas_quiz', methods=['POST'])
def add_respuestas_quiz():
    contenido = request.json.get("contenido", None)
    opcion = request.json.get("opcion", None)
    pregunta_id = request.json.get("pregunta_id", None)

    if not contenido:
       return jsonify({"msg": "contenido is required"}), 400
    
    if not pregunta_id:
        return jsonify({"msg": "pregunta_id is required"}), 400

    respuestass = Respuesta.query.filter_by(contenido=contenido).first()

    if respuestass:
        return jsonify({"msg": "Respuesta already exists"}), 400

    quiz_ids = Pregunta.query.filter_by(id=pregunta_id).first()

    if quiz_ids is None:
        return jsonify({"msg": "pregunta_id already not exists"}), 400

    respuesta = Respuesta()
    respuesta.opcion = opcion
    respuesta.contenido = contenido
    respuesta.pregunta_id = pregunta_id

    respuesta.guardar()

    return jsonify({"msg": "listo"}), 200
"""     
    return jsonify(respuesta.serialize()), 201 """
    
# .......................... OBTENER RESPUESTAS ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_respuestas/', methods=['GET'])
def get_respuestas():
    respuestas = Respuesta.query.all() 
    respuestas = list( map(lambda respuesta: respuesta.serialize(), respuestas)) 
    return jsonify(respuestas), 200

# .......................... OBTENER UNA RESPUESTAS ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/get_respuestas/<int:id>', methods=['GET'])
def get_respuestas_params(id):
    get = Respuesta.query.filter_by( id=id ).first()
    if get:
        return jsonify({get.serialize()}), 200
        

if __name__ == "__main__":
    manager.run()
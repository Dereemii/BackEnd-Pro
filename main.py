import datetime
from flask import Flask, jsonify, render_template, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
from models import db, User, Pregunta, Respuesta, Leccion, Teoria

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
        return jsonify({"msg": "Telefono is required"}), 400

    if not direccion:
        return jsonify({"msg": "Direccion is required"}), 400

    if not role_id:
        return jsonify({"msg": "Role_id is required"}), 400

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

# ..................... AGREGAR NOMBRE A LA LECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/agregar_nombre_leccion', methods=['POST'])
def agregar_nombre_leccion():
    nombre = request.json.get("nombre", None)

    if not nombre:
       return jsonify({"msg": "nombre es requerido"}), 400

    
    encontrar_nombre = Leccion.query.filter_by(nombre=nombre).first()

    if encontrar_nombre:
        return jsonify({"msg": "El Nombre Ya Existe"}), 400

    
    leccion = Leccion()
    leccion.nombre = nombre
    
    leccion.guardar()

    return jsonify(leccion.serialize()), 201

# ................... REGRESAR EL NOMBRE DE LA lECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_nombre_leccion', methods=['GET'])
def obtener_nombres_lecciones():
    lecciones = Leccion.query.all() 
    lecciones = list( map(lambda leccion: leccion.serialize(), lecciones)) 
    return jsonify(lecciones), 200

# ............. REGRESAR EL NOMBRE ESPECIFICO DE UNA LECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_nombre_leccion/<int:id>', methods=['GET'])
def obtener_nombre_especifico_leccion(id):
    leccion = Leccion.query.filter_by( id=id ).first()
    if leccion:
        return jsonify(leccion.serialize()), 200

# .................... AGREGAR PREGUNTAS AL QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/agregar_preguntas', methods=['POST'])
def agregar_preguntas():
    enunciado = request.json.get("enunciado", None)
    leccion_id = request.json.get("leccion_id", None)

    if not enunciado:
       return jsonify({"msg": "enunciado es requerido"}), 400

    if not leccion_id:
        return jsonify({"msg": "leccion_id es requerido"}), 400

    encontrar_enunciado = Pregunta.query.filter_by(enunciado=enunciado).first()

    if encontrar_enunciado:
        return jsonify({"msg": "El Enunciado ya existe"}), 400

    encontrar_leccion_id = Leccion.query.filter_by(id=leccion_id).first()

    if encontrar_leccion_id is None:
        return jsonify({"msg": "El leccion_id no existe"}), 400

    preguntas = Pregunta()

    preguntas.enunciado = enunciado
    preguntas.leccion_id = leccion_id

    preguntas.guardar()
            
    return jsonify(preguntas.serialize()), 201
    
# .................... OBTENER PREGUNTAS DE LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_pregunta', methods=['GET'])
def obtener_pregunta():
    preguntas = Pregunta.query.all() 
    preguntas = list( map(lambda pregunta: pregunta.serialize(), preguntas)) 
    return jsonify(preguntas), 201

# .................... OBTENER PREGUNTA ESPECIFICA DE LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_pregunta/<int:id>', methods=['GET'])
def obtener_pregunta_especifica(id):
    preguntas = Pregunta.query.filter_by(id=id).first()
    if preguntas:
        return jsonify(preguntas.serialize()), 201


# ..................... AGREGAR RESPUESTAS A LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/agregar_respuestas_leccion', methods=['POST'])
def agregar_respuestas_leccion():
    respuesta = request.json.get("respuesta", None)
    opcion = request.json.get("opcion", None)
    pregunta_id = request.json.get("pregunta_id", None)

    if not respuesta:
       return jsonify({"msg": "respuesta es requerido"}), 400
    
    if not opcion:
        return jsonify({"msg": "opcion es requerido"})

    if not pregunta_id:
        return jsonify({"msg": "pregunta_id es requerido"}), 400

    encontrar_respuesta = Respuesta.query.filter_by(respuesta=respuesta).first()

    if encontrar_respuesta:
        return jsonify({"msg": "La Respuesta ya existe"}), 400

    encontrar_pregunta_id = Pregunta.query.filter_by(id=pregunta_id).first()

    if encontrar_pregunta_id is None:
        return jsonify({"msg": "pregunta_id no existe"}), 400

    respuestas = Respuesta()
    respuestas.opcion = opcion
    respuestas.respuesta = respuesta
    respuestas.pregunta_id = pregunta_id

    respuestas.guardar()

    return jsonify(respuestas.serialize()), 201
    
# .......................... OBTENER RESPUESTAS ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_respuesta', methods=['GET'])
def obtener_respuesta():
    respuestas = Respuesta.query.all() 
    respuestas = list( map(lambda respuesta: respuesta.serialize(), respuestas)) 
    return jsonify(respuestas), 201

# .......................... OBTENER UNA RESPUESTA ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_respuesta/<int:id>', methods=['GET'])
def obtener_respuesta_especifica(id):
    respuestas = Respuesta.query.filter_by( id=id ).first()
    if respuestas:
        return jsonify(respuestas.serialize()), 201

# ..................... AGREGAR TEORIA DE LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/agregar_teoria', methods=['POST'])
def agregar_teoria():
    titulo = request.json.get("titulo", None)
    contenido = request.json.get("contenido", None)
    nombre_icono = request.json.get("nombre_icono", None)
    multimedia = request.json.get("multimedia", None)
    leccion_id = request.json.get("leccion_id", None)

    if not titulo:
        return jsonify({"msg": "titulo es requerido"}), 401
    if not contenido:
       return jsonify({"msg": "contenido es requerido"}), 401
    if not leccion_id:
       return jsonify({"msg": "leccion_id es requerido"}), 401
    encontrar_titulo = Teoria.query.filter_by( titulo=titulo ).first()
    if encontrar_titulo:
        return jsonify({"msg": "El Titulo ya existe"}), 401

    teoria = Teoria()
    teoria.titulo = titulo
    teoria.contenido = contenido
    teoria.nombre_icono = nombre_icono
    teoria.multimedia = multimedia
    teoria.leccion_id = leccion_id

    teoria.guardar()

    return jsonify(teoria.serialize()), 201

# ................... REGRESAR LAS TEORIAS DE LAS lECCIONES   ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_teoria', methods=['GET'])
def obtener_teorias():
    teorias = Teoria.query.all() 
    teorias = list( map(lambda teoria: teoria.serialize(), teorias)) 
    return jsonify(teorias), 201

# ................... REGRESAR LAS TEORIAS DE LAS lECCIONES   ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/api/obtener_teoria/<int:id>', methods=['GET'])
def obtener_teoria_especifica(id):
    teorias = Teoria.query.filter_by( id=id ).first()
    if teorias:
        return jsonify(teorias.serialize()), 201

if __name__ == "__main__":
    manager.run()
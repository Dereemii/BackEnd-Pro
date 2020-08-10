import os, datetime
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
from werkzeug.utils import secure_filename
from models import db, Usuario, Pregunta, Respuesta, Leccion, Teoria, Rol
from libs.utils import allowed_file

UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS_IMGS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_FILES = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True 
app.config['ENV'] = "development" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['JWT_SECRET_KEY'] = "0682f007844a0266990df1b2912f95bc"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# .......................... ADMINISTRAR USUARIOS............................
# _____________________________________________________________________________________________________________________________________________
@app.route('/usuarios', methods=['GET', 'POST'])
@app.route('/usuarios/<int:id>', methods=['GET', 'PUT', 'DELETE'])

def usuarios(id=None):
    if request.method == 'GET':
        if id is not None:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({"msj": "Usuario no encontrado"}), 404
            return jsonify(usuario.serialize()), 200
        else:
            usuarios = Usuario.query.all()
            usuarios = list(map(lambda usuario: usuario.serialize(), usuarios))
            return jsonify(usuarios), 200

# .......................... REGISTRO ....................................... 
# _____________________________________________________________________________________________________________________________________________    
@app.route('/registro', methods=['POST'])
def register():
    nombre_usuario = request.json.get("nombre_usuario", None)
    clave = request.json.get("clave", None)
    correo = request.json.get("correo", None)
    telefono = request.json.get("telefono", None)
    """ rol_id = request.json.get("rol_id", None) """

    if not nombre_usuario:
        return jsonify({"msg": "Se requiere un nombre de usuario"}), 400

    if not clave:
        return jsonify({"msg": "Se requiere una clave"}), 400

    if not correo:
        return jsonify({"msg": "Se requiere un correo"}), 400

    if not telefono:
        return jsonify({"msg": "Se requiere  un telefono"}), 400

    """ if not rol_id:
        return jsonify({"msg": "Se requiere un rol"}), 400 """

    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

    if usuario:
        return jsonify({"msg": "Nombre de usuario ya existe"}), 400

    usuario = Usuario()
    usuario.nombre_usuario = nombre_usuario
    usuario.correo = correo
    usuario.telefono = telefono
    usuario.clave = bcrypt.generate_password_hash(clave)
    """ usuario.password = bcrypt.generate_password_hash(clave).decode("utf-8") """

    usuario.guardar()

    return jsonify({"msg": "registro exitoso, por favor hacer login"}), 201

# .......................... LOGIN ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/login', methods=['POST'])
def login():
    correo = request.json.get("correo", None)
    clave = request.json.get("clave", None)

    if not correo:
        return jsonify({"msg": "Se requiere un correo"}), 400

    if not clave:
        return jsonify({"msg": "Se requiere una clave"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario:
        return jsonify({"msg": "correo/clave son incorrectos"}), 401

    if not bcrypt.check_password_hash(usuario.clave, clave):
        return jsonify({"msg": "correo/clave son incorrectos"}), 401

    expires = datetime.timedelta(days=3) # Duracion para el token

    datos = {
        "access_token": create_access_token(identity=usuario.correo, expires_delta=expires),
        "usuario": usuario.serialize() 
    }

    return jsonify({"succes": "Log In exitoso!", "datos": datos}), 200

# .......................... PERFIL ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/perfil', methods=['GET'])
@jwt_required
def perfil():
    correo = get_jwt_identity()
    usuario = Usuario.query.filter_by( correo=correo ).first()
    return jsonify(usuario.serialize_con_rol()), 200
 #   return jsonify({"msg": f"Perfil del usuario {nombre_usuario}", "usuario": usuario.serialize()}), 200

# ..................... AGREGAR NOMBRE A LA LECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/agregar_nombre_leccion', methods=['POST'])
def agregar_nombre_leccion():
    nombre = request.json.get("nombre", None)
    puntuacion = request.json.get("puntuacion", None)

    if not nombre:
       return jsonify({"msg": "nombre es requerido"}), 400

    if not puntuacion:
        return jsonify({"msg": "puntuacion es requerido"}), 400

    encontrar_nombre = Leccion.query.filter_by(nombre=nombre).first()

    if encontrar_nombre:
        return jsonify({"msg": "El Nombre Ya Existe"}), 400

    
    leccion = Leccion()
    leccion.nombre = nombre
    leccion.puntuacion = puntuacion
    
    leccion.guardar()

    return jsonify(leccion.serialize()), 201

# ................... REGRESAR EL NOMBRE DE LA lECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/obtener_nombre_leccion', methods=['GET'])
def obtener_nombres_lecciones():
    lecciones = Leccion.query.all() 
    lecciones = list( map(lambda leccion: leccion.serialize_con_teorias_y_preguntas(), lecciones)) 
    return jsonify(lecciones), 200

# ............. REGRESAR EL NOMBRE ESPECIFICO DE UNA LECCION ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/obtener_nombre_leccion/<int:id>', methods=['GET'])
def obtener_nombre_especifico_leccion(id):
    leccion = Leccion.query.filter_by( id=id ).first()
    if leccion:
        return jsonify(leccion.serialize_con_teorias_y_preguntas()), 200

# .................... AGREGAR PREGUNTAS AL QUIZ ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/agregar_preguntas', methods=['POST'])
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
@app.route('/obtener_pregunta', methods=['GET'])
def obtener_pregunta():
    preguntas = Pregunta.query.all() 
    preguntas = list( map(lambda pregunta: pregunta.serialize(), preguntas)) 
    return jsonify(preguntas), 201

# .................... OBTENER PREGUNTA ESPECIFICA DE LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/obtener_pregunta/<int:id>', methods=['GET'])
def obtener_pregunta_especifica(id):
    preguntas = Pregunta.query.filter_by(id=id).first()
    if preguntas:
        return jsonify(preguntas.serialize()), 201


# ..................... AGREGAR RESPUESTAS A LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/agregar_respuestas_leccion', methods=['POST'])
def agregar_respuestas_leccion():
    respuesta = request.json.get("respuesta", None)
    opcion = request.json.get("opcion", None)
    pregunta_id = request.json.get("pregunta_id", None)

    if not respuesta:
       return jsonify({"msg": "respuesta es requerido"}), 400
    
    if opcion is None:
        return jsonify({"msg": "opcion es requerido"}), 400
    
    if type(opcion) is not bool:
        return jsonify({"msg": "opcion es requerido"}), 400

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
@app.route('/obtener_respuesta', methods=['GET'])
def obtener_respuesta():
    respuestas = Respuesta.query.all() 
    respuestas = list( map(lambda respuesta: respuesta.serialize(), respuestas)) 
    return jsonify(respuestas), 201

# .......................... OBTENER UNA RESPUESTA ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/obtener_respuesta/<int:id>', methods=['GET'])
def obtener_respuesta_especifica(id):
    respuestas = Respuesta.query.filter_by( id=id ).first()
    if respuestas:
        return jsonify(respuestas.serialize()), 201

# ..................... AGREGAR TEORIA DE LA LECCION  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/agregar_teoria', methods=['POST'])
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
@app.route('/obtener_teoria', methods=['GET'])
def obtener_teorias():
    teorias = Teoria.query.all() 
    teorias = list( map(lambda teoria: teoria.serialize(), teorias)) 
    return jsonify(teorias), 201

# ................... REGRESAR LAS TEORIAS DE LAS lECCIONES   ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/obtener_teoria/<int:id>', methods=['GET'])
def obtener_teoria_especifica(id):
    teorias = Teoria.query.filter_by( id=id ).first()
    if teorias:
        return jsonify(teorias.serialize()), 201

# ................... GUARDAR IMAGEN DE PERFIL   ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/fotoperfil', methods=["POST"])
@jwt_required
def fotoperfil():
    if 'avatar' not in request.files:
        return jsonify({"msg": "Avatar es requerido"}), 401

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"msg": "No seleccionaste el archivo"}), 401

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMGS):

        correo = get_jwt_identity()
        usuario = Usuario.query.filter_by( correo=correo ).first()

        filename = secure_filename(file.filename)
        filename = "usuario_" + str(usuario.id) + "_" + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER']+"/imagenes", filename))

        usuario.avatar = filename
        usuario.actualizar()

        return jsonify({"msg": "imagen de perfil guardada satisfactoriamente"}), 200
    return jsonify({"msg": "imagen de perfil no pudo guardarse"}), 400

@app.route('/fotoperfil/<filename>')
def foto_perfil(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER']+"/imagenes", filename), 200
    
# ................... ROLES TANTO PARA TODOS COMO PARA UNO EN ESPECIFICO  ....................................... 
# _____________________________________________________________________________________________________________________________________________
@app.route('/rol', methods=['GET', 'POST'])
@app.route('/rol/<int:id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def todos_los_roles(id=None):

#----------------------------- METODO GET --------------------------------------------------

    if request.method == "GET":
        if id is not None:
            rol = Rol.query.get(id)
            if rol:
                return jsonify(rol.serialize()), 205
            return jsonify({'msg': 'Este rol no existe'}), 405
        else:
            roles = Rol.query.all()
            roles = list(map(lambda rol: rol.serialize(), roles))
            return jsonify(roles), 205

#------------------------------ METODO PUT ------------------------------------------------
    
    elif request.method == 'PUT':
        roles = Rol.query.get(id)
        roles.rol = request.json.get("rol","")

        roles.actualizar()
        return jsonify({"msg": "Actualizado satisfactoriamente"}), 205

#------------------------------ METODO DELETE -------------------------------------------------

    elif request.method == "DELETE":
        rol = Rol.query.get(id)
        
        rol.borrar()
        return jsonify({"msg": "Borrado satisfactoriamente"}), 205

#------------------------------ METODO POST ----------------------------------------------

    elif request.method == "POST":
        rol = Rol()
        rol.rol = request.json.get("rol","")
        rol.usuario_id = request.json.get("usuario_id","")

        rol.guardar()
        return jsonify(rol.serialize()), 205

if __name__ == "__main__":
    manager.run()
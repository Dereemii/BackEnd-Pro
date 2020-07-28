from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=True, unique=True)
    password = db.Column(db.String(120), nullable=True)
    nombre = db.Column(db.String(120), nullable=True)
    apellido = db.Column(db.String(120), nullable=True)
    edad = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    telefono = db.Column(db.Integer, nullable=True, unique=True)
    direccion = db.Column(db.String(120), nullable=True)
    role_id = db.Column(db.Integer, nullable=True)
    """ puntos_de_experiencia = db.Column(db.Integer, nullable=True) """

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "edad": self.edad,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "role_id": self.role_id,
        }

class Curso(db.Model):
    __tablename__= "curso"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=True, unique=True)
    nivel_del_curso = db.Column(db.String(100), nullable=True)
    contenido = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    fecha = db.Column(db.String(50), nullable=True)

class Cursos_Inscritos(db.Model):
    __tablename__= "cursos_inscritos"
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.String(100), nullable=True)
    fecha_inscripcion = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean)

class Progreso_Curso(db.Model):
    __tablename__= "progreso_curso"
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.String(100), nullable=True)
    puntos_experiencia = db.Column(db.String(100), nullable=True)
    fecha_creacion = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Boolean, nullable=True)

class Role(db.Model):
    __tablename__= "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=True)

class Aprovacion_del_Quiz(db.Model):
    __tablename__= "aprovacion_del_quiz"
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.String(500), nullable=True)
    completado = db.Column(db.Boolean, nullable=True)

class Ranking(db.Model):
    __tablename__= "ranking"
    id = db.Column(db.Integer, primary_key=True)
    puntaje = db.Column(db.String(120), nullable=True)

class Quiz(db.Model):
    __tablename__= "quiz"
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, nullable=True)
    preguntas = db.Column(db.String(120), nullable=True)

class Respuestas_Quiz(db.Model):
    __tablename__= "respuestas_quiz"
    id = db.Column(db.Integer, primary_key=True)
    respuestas_correctas = db.Column(db.String(120), nullable=True)
    pregunta_id = db.Column(db.String(120), nullable=True)

class Preguntas_Quiz(db.Model):
    __tablename__= "preguntas_quiz"
    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.String(120), nullable=True)

class Respuestas_Usuario(db.Model):
    __tablename__= "respuestas_usuario"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=True)
    pregunta_id = db.Column(db.String(120), nullable=True)
    respuesta_usuario = db.Column(db.String(120), nullable=True)



from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression
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
#

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



       # EJEMPLO !!!!!!! 
#   _________________________________________________________________________________________

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    addresses = db.relationship('Address', backref='person', lazy=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

#   ______________________________________________________________________________________


class Quiz(db.Model):
    __tablename__= "quiz"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=True, unique=True)
    preguntas = db.relationship("Pregunta", backref=("quiz"), lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
        }

    def guardar(self):
        db.session.add(self)
        db.session.commit()
    
    def actualizar(self):
        db.session.commit()

    def borrar(self):
        db.session.delete(self)
        db.session.commit()

class Pregunta(db.Model):
    __tablename__= "preguntas"
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    pregunta = db.Column(db.String(120), nullable=True, unique=True)
    respuestas = db.relationship("Respuesta", backref="preguntas", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "pregunta": self.pregunta,
            "quiz": {
                "id": self.quiz.id,
                "titulo": self.quiz.titulo
            }
        }
  
    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def actualizar(self):
        db.session.commit()
    
    def borrar(self):
        db.session.delete(self)
        db.session.commit()

class Respuesta(db.Model):
    __tablename__= "respuestas"
    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey("preguntas.id"), nullable=False)
    contenido = db.Column(db.String(120), nullable=True)
    opcion = db.Column(db.String(120), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "contenido": self.contenido,
            "opcion": self.opcion,
            "pregunta": {
                "id": self.preguntas.id,
                "pregunta": self.preguntas.pregunta,
                "quiz": {
                    "id": self.preguntas.quiz.id,
                    "titulo": self.preguntas.quiz.titulo
                }
            }
        }

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def actualizar(self):
        db.session.commit()

    def borrar(self):
        db.session.delete(self)
        db.session.commit()


""" 
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

class Respuestas_Usuario(db.Model):
    __tablename__= "respuestas_usuario"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=True)
    pregunta_id = db.Column(db.String(120), nullable=True)
    respuesta_usuario = db.Column(db.String(120), nullable=True) """



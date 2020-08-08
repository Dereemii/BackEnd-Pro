from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(120), nullable=False, unique=True)
    correo = db.Column(db.String(120), nullable=False, unique=True)
    clave = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.Integer, nullable=True, unique=True)
    avatar = db.Column(db.String(100), default="sin-foto.png")
    activo = db.Column(db.Boolean, default=True)
    puntos_experiencia = db.Column(db.Integer, nullable=True, default=0)
    rol = db.relationship("Rol", backref=("usuarios"), lazy=True, uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "correo": self.correo,
            "telefono": self.telefono,
            "activo": self.activo
        }

    def serialize_con_rol(self):
        rol = list(map(lambda roles: roles.serialize(), [self.rol]))
        return {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "correo": self.correo,
            "telefono": self.telefono,
            "activo": self.activo,
            "rol": rol
        }

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def actualizar(self):
        db.session.commit()
    
    def borrar(self):
        db.session.delete(self)
        db.session.commit()

class Rol(db.Model):
    __tablename__= "roles"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "rol": self.rol
        }
    
    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def actualizar(self):
        db.session.commit()
    
    def borrar(self):
        db.session.delete(self)
        db.session.commit()

class Leccion(db.Model):
    __tablename__= "lecciones"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    puntuacion = db.Column(db.Integer, nullable=False)
    pregunta = db.relationship("Pregunta", backref=("lecciones"), lazy=True)
    teoria = db.relationship("Teoria", backref=("lecciones"), lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "puntuacion": self.puntuacion,
        }

    def serialize_con_teorias_y_preguntas(self):
        pregunta = list(map(lambda preguntas: preguntas.serialize_con_preguntas(), self.pregunta))
        teoria = list(map(lambda teorias: teorias.serialize_para_leccion(), self.teoria))
        return {
            "id": self.id,
            "nombre": self.nombre,
            "puntuacion": self.puntuacion,
            "preguntas": pregunta,
            "teoria": teoria
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
    enunciado = db.Column(db.String(120), nullable=False, unique=True)
    leccion_id = db.Column(db.Integer, db.ForeignKey("lecciones.id"), nullable=False)
    respuesta = db.relationship("Respuesta", backref="preguntas", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "enunciado": self.enunciado,
            "leccion": {
                "id": self.lecciones.id,
                "nombre": self.lecciones.nombre
            }
        }

    def serialize_con_preguntas(self):
        respuesta = list(map(lambda respuestas: respuestas.serialize(), self.respuesta))
        return {
            "id": self.id,
            "enunciado": self.enunciado,
            "respuestas": respuesta
        }
  
    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def actualizar(self):
        db.session.commit()
    
    def borrar(self):
        db.session.delete(self)
        db.session.commit()

class Teoria(db.Model):
    __tablename__= "teorias"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False, unique=True)
    contenido = db.Column(db.String(500), nullable=False)
    nombre_icono = db.Column(db.String(120), nullable=True, default=None)
    multimedia = db.Column(db.String(120), nullable=True, default=None)
    leccion_id = db.Column(db.Integer, db.ForeignKey('lecciones.id'), nullable=False)

    def serialize(self):
        return {
            "titulo":self.titulo,
            "contenido":self.contenido,
            "nombre_icono":self.nombre_icono,
            "multimedia":self.multimedia,
            "leccion":{
                "id":self.lecciones.id,
                "nombre":self.lecciones.nombre,
            }
        }

    def serialize_para_leccion(self):
        return {
            "titulo":self.titulo,
            "contenido":self.contenido,
            "nombre_icono":self.nombre_icono,
            "multimedia":self.multimedia
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
    respuesta = db.Column(db.String(120), nullable=False)
    opcion = db.Column(db.Boolean, nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey("preguntas.id"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "respuesta": self.respuesta,
            "opcion": self.opcion,
            "pregunta": {
                "id": self.preguntas.id,
                "enunciado": self.preguntas.enunciado,
                "leccion": {
                    "id": self.preguntas.lecciones.id,
                    "nombre": self.preguntas.lecciones.nombre
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

class Aprobacion_del_Quiz(db.Model):
    __tablename__= "aprobacion_del_quiz"
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


"""             "usuario": {
                "id": self.usuarios.id,
                "nombre_usuario": self.usuarios.nombre_usuario,
                "correo": self.usuarios.correo,
                "telefono": self.usuarios.telefono,
                "activo": self.usuarios.activo,
            }, """
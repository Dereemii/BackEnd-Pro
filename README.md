# Diagrama:
para correrlo ejecutar:
    python main.py db migrate
    python main.py db upgrade




# Curso
-
id int PK FK >- Quiz.id
title string unique
nivel_curso string
autor string
content string
status boolean
date timestamp

# User
-
id int PK
nombre_usuario string
password string
name string
lastname string
age int
email string unique
phone int
addres string
role_id int FK >- Role.id
puntos_experiencia number


# Cursos_inscritos
-
curso_id int FK >- Curso.id
id int PK 
user_id int FK >- User.id
fecha timestamp
status boolean

# Progreso_Curso
-
curso_id int PK FK >- User.puntos_experiencia
created_at datetime 
preguntas
respuestas
status enum("completed","in progress")

# Quiz
-
id integer PK
curso_id int PK FK >- Progreso_Curso.curso_id
preguntas string FK >- Aprobacion_del_Quiz.completado
respuestas string FK >- Aprobacion_del_Quiz.completado

# Role
-
id int 
name string

# Aprobación_del_Quiz
-
id integer pk
completado boolean FK >- Progreso_Curso.curso_id

# Ranking
-
id integer PK FK >- User.id
puntaje string

# Quiz
-
id integer PK
curso_id int PK
preguntas string FK -< Preguntas_Quiz

# Respuestas_Quiz
-
id pk integer
respuestas_correcta string
pregunta_id string FK >- Preguntas_Quiz.id

# Preguntas_Quiz
-
id pk integer
enunciado string

# Respuesta_Usuario
-
id pk integer
user_id string
pregunta_id string FK >- Preguntas_Quiz.id
respuesta_usuario string

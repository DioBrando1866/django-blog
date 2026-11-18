# Blog en Django (migrado desde Symfony 6.4)

## 1. Dependencias del sistema (Ubuntu)
    sudo apt update
    sudo apt install -y pkg-config default-libmysqlclient-dev build-essential python3-dev

## 2. Entorno virtual y paquetes
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## 3. Base de datos (desde DBeaver)
Crea una base de datos nueva y vacía:

    CREATE DATABASE blog_django CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

## 4. Credenciales de MySQL (variables de entorno)
    export DB_USER=root
    export DB_PASSWORD='tu_contraseña'
    export DB_HOST=127.0.0.1      # IP del servidor MySQL si no está en esta máquina
    export DB_NAME=blog_django

## 5. Crear tablas, superusuario y arrancar
    python manage.py makemigrations blog
    python manage.py migrate
    python manage.py createsuperuser      # pide email, name y contraseña
    python manage.py runserver

Abre http://127.0.0.1:8000/

## Rutas
| Symfony            | Django                         |
|--------------------|--------------------------------|
| /                  | /                              |
| /about, /contact   | /about/, /contact/             |
| /blog, /blog/{n}   | /blog/?page=n                  |
| /blog/buscar       | /blog/?searchTerm=texto        |
| /blog/new          | /blog/new/                     |
| /single_post/{slug}| /single_post/<slug>/           |
| .../like           | /single_post/<slug>/like/ (POST)|
| /login /register   | /login/ /register/             |
| /admin/images      | /admin/images/                 |
| /admin/categories  | /admin/categories/             |
| (no existía)       | /django-admin/ (panel de Django)|

El usuario admin se crea con `createsuperuser` (equivale a ROLE_ADMIN).

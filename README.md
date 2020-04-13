# Les Grandes Oreilles

Bienvenue sur le projet de gestion de la pension refuge Les Grandes Oreilles.

## Installation

Créez un environnement virtuel Python

    mkvirtualenv lesgrandesoreilles

Activez l'environnement avec

    workon lesgrandesoreilles

Installez les dépendances

	pip install -r requirements.txt

## Pour lancer le projet

Activez l'environnement avec

	workon lesgrandesoreilles

Mettez à la jour la base de données

    ./manage.py migrate

Créez un administrateur

	./manage.py createsuperuser

Lancez le serveur

	./manage.py runserver

Enjoy! http://localhost:8000/admin_interface/

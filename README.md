# Foodgram - A story about cooking!!


### What is there:
- Ability to share your recipes
- See other users' recipes
- Add recipes to favorites
- Watch what your friends and colleagues have added

### Stack:
- Python
- Django
- Docker

### Project Launch:
1. Clone the project:
``
git clone https://github.com/coolslive/foodgram-project-react.git
``
2. Prepare the server:
`
scp docker-compose.yml <username>@<host>:/home page/<username>/
scp nginx.conf <username>@<host>:/home page/<username>/
scp .env <username>@<host>:/home page/<username>/
``
3. Install docker and docker-compose:
``

installing sudo apt docker.io sudo apt installs docker-compose
``
4. Assemble the container and perform migrations:
``
sudo docker-compose up -d --build
sudo docker-compose exec of the python backend manage.py migrate
``
5. Create a superuser and collect static:
``
sudo docker-compose exec server management on python.py createsuperuser
sudo docker-compose exec python server part manage.py collectstatic -without input
``
6. Copy the pre-loaded json data:
``
sudo docker-compose exec server part in python manage.py loadmodels --path 'recipes/data/ingredients.json'
sudo docker-compose exec python backend manage.py loadmodels --path 'recipes/data/tags.json'
```

### Author:
**Vyacheslav Erlich**
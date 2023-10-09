
# Проект Foodgram


## Описание:
- Возможность делиться своими рецептами
- Смотрите рецепты других пользователей
- Добавляйте рецепты в избранное
- Следите за тем, что добавили ваши друзья и коллеги

## Технологии:
- Python
- Django
- Docker

## Установка:


1. Подготовка сервера:
```
scp docker-compose.yml <username>@<host>:/home page/<username>/
scp nginx.conf <username>@<host>:/home page/<username>/
scp .env <username>@<host>:/home page/<username>/

```
2. Устанавливаем docker and docker-compose:
```

installing sudo apt docker.io sudo apt installs docker-compose
```
3. Собераем контейнер и выполняем миграцию:
```
sudo docker-compose up -d --build
sudo docker-compose exec of the python backend manage.py migrate
```
4. Создаем суперпользователя и собираем статические данные:
```
sudo docker-compose exec server management on python.py createsuperuser
sudo docker-compose exec python server part manage.py collectstatic -without input
```
5. Скопируем предварительно загруженные данные в формате json:
```
sudo docker-compose exec server part in python manage.py loadmodels --path 'recipes/data/ingredients.json'
sudo docker-compose exec python backend manage.py loadmodels --path 'recipes/data/tags.json'
```

## Автор:
Вячеслав Эрлих

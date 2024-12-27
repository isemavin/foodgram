![status workflow](https://github.com/isemavin/foodgram/actions/workflows/main.yml/badge.svg)
## Проект Foodgram
---
#### Foodgram — это онлайн-платформа, где любители кулинарии могут делиться своими любимыми рецептами, вдохновляться идеями других пользователей и находить новые вкусовые сочетания. Здесь каждый найдет что-то интересное: от простых домашних блюд до изысканных ресторанных шедевров. Присоединяйтесь к сообществу Foodgram, чтобы обмениваться опытом, учиться новому и наслаждаться процессом приготовления пищи вместе!
##### Cсылка на сайт: https://gorilblin.zapto.org
---
### Приложение Foodgram использует следующие технологии:
```Python``` ```Django``` ```Django Rest Framework``` ```PostgreSQL``` ```Nginx``` ```Gunicorn``` ```Docker``` ```GitHub Actions``` ```Continuous Integration``` ```Continuous Deployment```

---
### Как развернуть проект:
1) Клонируйте репозиторий:
```
git clone git@github.com:isemavin/foodgram.git
```
2) Перейдите в корневую папку проекта:
```
cd foodgram
```
3) Создайте файл __.env__ и заполните его:
```
POSTGRES_USER=<Имя пользователя>
POSTGRES_PASSWORD=<Пароль>
POSTGRES_DB=<База данных>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<Секретный ключ django>
DEBUG=<True/False>
ALLOWED_HOSTS=<хосты>
```
4) Запустите docker-compose.production:
```
docker compose -f docker-compose.production.yml up
```
5) Выполните миграции, создайте суперпользователя, загрузите фикстуры, сбор статики:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
docker compose -f docker-compose.production.yml exec backend python manage.py load_fixtures ingredients.json ingredients
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```
6) Установите веб-сервер. В примере будет использоваться веб-сервер nginx.
```
sudo apt install nginx -y
sudo systemctl start nginx
```
7) Измените файл конфигурации Nginx в редакторе:
```sudo nano /etc/nginx/sites-enabled/default```

```
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
}
```
8) Проверьте правильность конфигурации Nginx:

    ```sudo nginx -t```

9) Перезапустите Nginx:

    ```sudo service nginx reload```
---
#### Настройка CI/CD
В проекте для поддержания прицнипа CI/CD используется технология GitHub Actions.
В репозитории уже настроен процесс автоматиации.

Для работы workflow добавьте секреты в GitHub Actions:
```DOCKER_USERNAME``` - имя пользователя в DockerHub
```DOCKER_PASSWORD``` - пароль пользователя в DockerHub
```HOST``` - IP-адрес сервера
```USER``` - имя пользователя
```SSH_KEY``` - содержимое приватного SSH-ключа 
```SSH_PASSPHRASE``` - пароль для SSH-ключа
```TELEGRAM_TO``` - id пользователя, которому бот отправит сообщения о деплое
```TELEGRAM_TOKEN``` - токен телеграм бота

---
#### Запуск проекта локально
1) Клонируйте репозиторий:
```
git clone git@github.com:isemavin/foodgram.git
```
2) Перейдите в папку:
```
cd foodgram/backend
```
3) Настройка виртуального окружения:
- Cоздать и активировать виртуальное окружение: ```python3 -m venv env``` ```source env/bin/activate```
- Установить зависимости из файла requirements.txt: ```python -m pip install --upgrade pip``` ```pip install -r requirements.txt```
4) Создайте файл __.env__ и заполните его:
```
POSTGRES_USER=<Имя пользователя>
POSTGRES_PASSWORD=<Пароль>
POSTGRES_DB=<База данных>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<Секретный ключ django>
DEBUG=<True/False>
ALLOWED_HOSTS=<хосты>
```
5) Выполните миграции и создайте суперпользователя:
```python manage.py migrate``` ```python manage.py createsuperuser```
6) Загрузка фиустур: ```python manage.py load_fixtures ingredients.json ingredients```
7) Запуск сервера ```python manage.py runserver```
Документация будет доступна по адресу: http://localhost/api/docs/
---
#### Автор проекта: Семавин Илья Игоревич https://github.com/isemavin
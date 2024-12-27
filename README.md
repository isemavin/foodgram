![status workflow](https://github.com/isemavin/foodgram/actions/workflows/main.yml/badge.svg)
## Проект Foodgram
---
#### Foodgram — это онлайн-платформа, где любители кулинарии могут делиться своими любимыми рецептами, вдохновляться идеями других пользователей и находить новые вкусовые сочетания. Здесь каждый найдет что-то интересное: от простых домашних блюд до изысканных ресторанных шедевров. Присоединяйтесь к сообществу Foodgram, чтобы обмениваться опытом, учиться новому и наслаждаться процессом приготовления пищи вместе!
---
### Приложение Foodgram использует следующие технологии:
- __Python__ — основной язык программирования.
- __Docker__ — для контейнеризации приложения.
- __GitHub Actions__ — для автоматизации CI/CD процесса.
- __Git__ — как система управления версиями.
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
5) Выполните миграции, сбор статики:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```
__Примеры запросов к API:__
Эндпоинт для просомтра всех рецептов: https://gorilblin.zapto.org/recipes
Метод: __GET__
Ответ:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
Эндпоинт для просомтра подписок: https://gorilblin.zapto.org/subscriptions
Метод: __GET__
Ответ:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.png",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0,
      "avatar": "http://foodgram.example.org/media/users/image.png"
    }
  ]
}
```
---
#### Автор проекта: Илья Семавин https://github.com/isemavin
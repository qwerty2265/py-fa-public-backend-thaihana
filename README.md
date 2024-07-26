# badback

## python
python 3.8 (https://www.python.org/downloads/release/python-380/)

## pip
```
pip install
alembic
asyncpg
uvicorn
fastapi[all]
python-slugify
requests
phonenumbers
python-multipart
```

## postgres 
postgresql + pgAdmin (https://www.postgresql.org/)

Standart Install

## pgadmin quick start
Add New Server

General > Name: postgres

Connection > Host name: localhost

Connection > Password: postgres

## env
create file .env in project root

fill with:
```
DEBUG=True

SECRET=PIVO

LIMIT=50

DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=postgres

TELEGRAM_API_KEY=
TELEGRAM_CHAT_ID=

IMAGE_PATH="./images"
```

## Pull & First start
```
git pull
alembic upgrade head
```

## Start
```
uvicorn main:app --reload
```

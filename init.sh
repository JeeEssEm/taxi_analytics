#!/bin/bash

echo "Запуск контейнеров..."
docker-compose up -d db

echo "Ожидание запуска базы данных..."
sleep 10

echo "Создание и применение миграций..."
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate

echo "Запуск приложения..."
docker-compose up web

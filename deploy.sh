#!/bin/bash

# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Запуск приложения (например, через gunicorn)
gunicorn app:app --bind 0.0.0.0:$PORT

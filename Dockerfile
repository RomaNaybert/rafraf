# Используем базовый образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Прокидываем порт (если используешь Flask по умолчанию 5000)
EXPOSE 5000

# Запускаем приложение
CMD ["python3", "app.py"]

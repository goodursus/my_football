# Используем официальный образ Python
FROM python:3.12.6-slim

# Устанавливаем рабочую директорию
WORKDIR /my_football

# Копируем файлы в контейнер
COPY . /my_football

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8050
EXPOSE 8050

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:server"]

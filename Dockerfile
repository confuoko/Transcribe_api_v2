# Используем официальный образ Python 10 как базовый
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /Transcribe_api_v2

# Копируем файл зависимостей в контейнер (если он есть)
COPY requirements.txt /Transcribe_api_v2/

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер в папку /Transcribe_api_v2
COPY . /Transcribe_api_v2

# Открываем порты (если нужно для вашего приложения)
EXPOSE 8000

# Указываем команду для запуска вашего приложения
CMD ["python", "main.py"]

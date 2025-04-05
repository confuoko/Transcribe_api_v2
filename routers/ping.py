from fastapi import APIRouter
from pydantic import BaseModel
from services.transcribe_service import processFile

import boto3
import os
from tempfile import NamedTemporaryFile
router = APIRouter()

@router.get("/ping", summary="Ping-Pong API", tags=["Health Check"])
def ping():
    """
    Простая проверка доступности сервиса.
    Возвращает 'pong'.
    """
    return {"message": "pong"}

class AudioRequest(BaseModel):
    audio_url: str


@router.post("/audio", summary="Принять ссылку на аудио", tags=["Audio"])
def process_audio(request: AudioRequest):
    """
    Обрабатывает аудио-ссылку и возвращает подтверждение.
    """
    bucket_name = "audiotest"
    file_key = request.audio_url

    # Создаем сессию для подключения к MinIO через S3 API
    s3 = boto3.client('s3',
                      endpoint_url='http://127.0.0.1:9000',
                      aws_access_key_id='admin',
                      aws_secret_access_key='adminpassword',
                      region_name='us-east-1')

    # Загружаем файл из S3 в временный файл
    file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)

    # Путь к временной папке "temp" в директории проекта
    temp_dir = os.path.join(os.getcwd(), 'temp')

    # Создаем путь для временного файла в папке temp
    temp_file_path = os.path.join(temp_dir, file_key)

    # Записываем данные из объекта в файл
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_obj['Body'].read())

    print(f'Файл сохранен во временную папку: {temp_file_path}')

    # Передаем путь к файлу в processFile
    print("Начинаю транскрибацию")
    answer = processFile(temp_file_path)

    # Удаляем временный файл после обработки
    os.remove(temp_file_path)

    return {"message": f"Ваша аудиозапись: {answer}"}
from fastapi import APIRouter
from pydantic import BaseModel
from services.transcribe_service import processFile

import boto3
import os
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
import torch
load_dotenv()


if torch.cuda.is_available():
    print("✅ CUDA доступна (используется GPU)")
else:
    print("❌ CUDA недоступна (используется CPU)")



router = APIRouter()


@router.get("/cpu", summary="Ping-Pong API", tags=["Health Check"])
def ping():
    """
    Простая проверка доступности сервиса.
    Возвращает 'pong' и информацию об устройстве.
    """
    if torch.cuda.is_available():
        answer = "✅ CUDA доступна (используется GPU)"
    else:
        answer = "❌ CUDA недоступна (используется CPU)"

    return {"message": answer}

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
    """
    bucket_name = "audiotest"
    file_key = request.audio_url

    # Создаем сессию для подключения к MinIO через S3 API
    s3 = boto3.client('s3',
                      endpoint_url='http://127.0.0.1:9000',
                      aws_access_key_id='admin',
                      aws_secret_access_key='adminpassword',
                      region_name='us-east-1')
    """
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    bucket_name = "whisper-audiotest"
    file_key = request.audio_url

    # Создаем сессию для подключения к MinIO через S3 API
    s3 = boto3.client('s3',
                      endpoint_url="http://storage.yandexcloud.net",
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                      )
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
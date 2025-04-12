from fastapi import APIRouter
from pydantic import BaseModel
from services.transcribe_service import processFile
import time
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

    file_key = request.audio_url
    load_dotenv()
    torch_variable = str(torch.cuda.is_available())
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = "whisper-audiotest"

    s3 = boto3.client(
        's3',
        endpoint_url="http://storage.yandexcloud.net",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file_key)

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_obj['Body'].read())

    print(f'📁 Файл сохранён во временную папку: {temp_file_path}')

    # === Засекаем время ===
    print("🧠 Начинаю транскрибацию...")
    start_time = time.time()
    answer = processFile(temp_file_path)
    duration = round(time.time() - start_time, 2)  # Время в секундах с округлением
    print(f"✅ Готово за {duration} секунд.")

    # === Генерируем имя текстового файла ===
    text_filename = os.path.splitext(file_key)[0] + ".txt"
    text_file_path = os.path.join(temp_dir, text_filename)

    # === Сохраняем текст во временный .txt файл ===
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(answer)
        f.write(f"\n\n⏱️ Файл был обработан за {duration} секунд.")
        f.write(f"\n\n⏱️ Доступность CUDA: {torch_variable}.")

    print(f"📝 Ответ сохранён в файл: {text_file_path}")

    # === Загружаем .txt обратно в S3 ===
    s3.upload_file(
        Filename=text_file_path,
        Bucket=bucket_name,
        Key=text_filename
    )
    print(f"☁️ Файл {text_filename} загружен в S3 (в корень бакета)")

    # === Удаляем временные файлы ===
    os.remove(text_file_path)
    os.remove(temp_file_path)
    print("🧹 Временные файлы удалены.")

    return {"message": f"Ваша аудиозапись: {answer}"}
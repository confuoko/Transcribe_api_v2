from fastapi import FastAPI
from views import api_router

app = FastAPI(
    title="My API",
    description="Простое API с маршрутом /ping",
    version="1.0.0"
)
#uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# Подключаем все маршруты
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


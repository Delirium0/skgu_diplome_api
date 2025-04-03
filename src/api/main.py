from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.locations.router import router as router_locations
from src.api.search.router import router as router_search
from src.api.schedule.router import router as schedule_router
from src.api.services.important_links.router import router as important_links

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых источников (можно указать конкретные домены)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)
app.include_router(router_search)
app.include_router(router_locations)
app.include_router(schedule_router)
app.include_router(important_links)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

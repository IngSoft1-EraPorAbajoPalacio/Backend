from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from db.base import engine
from db.models import * 
from routers import partida
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.drop_all(bind=engine)  # Elimina todas las tablas
#Base.metadata.create_all(bind=engine) # Crea todas las tablas

app = FastAPI(title="El Switcher")

app.include_router(partida.router)

@app.get("/")
def root() :
    return RedirectResponse(url='/docs/')   

origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



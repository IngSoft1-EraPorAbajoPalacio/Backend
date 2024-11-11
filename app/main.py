from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.db.base import engine
from app.db.models import * 
from app.routers import partida, juego, ws
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # Crea todas las tablas
    yield
    Base.metadata.drop_all(bind=engine) # Elimina todas las tablas
    
app = FastAPI(title="El Switcher", lifespan=lifespan)

app.include_router(partida.router)
app.include_router(juego.router)
app.include_router(ws.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() :
    return RedirectResponse(url='/docs/')   



    
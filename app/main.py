from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.db.base import engine
from app.db.models import * 
from app.routers import partida, juego
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="El Switcher")

app.include_router(partida.router)
app.include_router(juego.router)


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


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine) # Crea todas las tablas

@app.on_event("shutdown")
def shutdown_event():
    Base.metadata.drop_all(bind=engine) # Elimina todas las tablas
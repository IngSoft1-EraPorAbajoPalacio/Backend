from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from db.base import engine
from db.models import * 
from routers import partida
from fastapi.middleware.cors import CORSMiddleware


#Base.metadata.drop_all(bind=engine)  # Elimina todas las tablas
Base.metadata.create_all(bind=engine) # Crea todas las tablas

app = FastAPI(title="El Switcher")

app.include_router(partida.router)


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


from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from db.base import engine
from db.models import Base 

#Base.metadata.drop_all(bind=engine)  # Elimina todas las tablas
Base.metadata.create_all(bind=engine) # Crea todas las tablas

app = FastAPI(title="El Switcher")


@app.get("/")
def root() :
    return RedirectResponse(url='/docs/')   

#if __name__ == "__main__":
#    run("main:app",host="0.0.0.0", reload=True, port=8000)
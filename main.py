from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import inicializar_bd
from routers import auth, plataformas, juegos

# Gestor de ciclo de vida moderno (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el servidor
    inicializar_bd()
    yield
    # Código opcional para cuando se apague el servidor

app = FastAPI(
    title="API Rest - Gestión de Juegos y Plataformas (PM1-AA1-EV03)",
    description="Sistema CRUD con SQLite3, Pydantic, routers, JWT y control por roles.",
    version="1.0.0",
    lifespan=lifespan
)

# Inclusión de routers
app.include_router(auth.router)
app.include_router(plataformas.router)
app.include_router(juegos.router)

@app.get("/", tags=["General"])
def endpoint_raiz():
    return {
        "mensaje": "Bienvenido a la API REST de Plataformas y Juegos",
        "docs": "/docs"
    }
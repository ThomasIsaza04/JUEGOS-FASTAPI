from typing import Optional
from pydantic import BaseModel, Field

# --- ESQUEMAS DE AUTENTICACIÓN ---
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# --- ESQUEMAS DE PLATAFORMAS (ENTIDAD PRINCIPAL) ---
class PlataformaBase(BaseModel):
    nombre: str = Field(..., min_length=2, example="PlayStation 5")
    fabricante: str = Field(..., min_length=2, example="Sony")
    anio_lanzamiento: int = Field(..., ge=1970, le=2030, example=2020)


class PlataformaResponse(PlataformaBase):
    id: int


class PlataformaUpdate(BaseModel):
    nombre: Optional[str] = None
    fabricante: Optional[str] = None
    anio_lanzamiento: Optional[int] = None


# --- ESQUEMAS DE JUEGOS (ENTIDAD DEPENDIENTE) ---
class JuegoBase(BaseModel):
    titulo: str = Field(..., min_length=1, example="God of War Ragnarök")
    genero: str = Field(..., min_length=2, example="Acción / Aventura")
    precio: float = Field(..., ge=0.0, example=69.99)
    es_multijugador: bool = Field(default=False, example=False)
    plataforma_id: int = Field(..., gt=0, example=1)


class JuegoResponse(JuegoBase):
    id: int


class JuegoUpdate(BaseModel):
    titulo: Optional[str] = None
    genero: Optional[str] = None
    precio: Optional[float] = None
    es_multijugador: Optional[bool] = None
    plataforma_id: Optional[int] = None
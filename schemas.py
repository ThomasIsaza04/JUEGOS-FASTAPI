from typing import Optional, List
from pydantic import BaseModel, Field

# --- ESQUEMAS DE AUTENTICACIÓN ---
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# --- ESQUEMAS DE PLATAFORMAS (ENTIDAD PRINCIPAL) ---
class PlataformaBase(BaseModel):
    nombre: str = Field(..., min_length=2, json_schema_extra={"example": "PlayStation 5"})
    fabricante: str = Field(..., min_length=2, json_schema_extra={"example": "Sony"})
    anio_lanzamiento: int = Field(..., ge=1970, le=2030, json_schema_extra={"example": 2020})


class PlataformaCreate(PlataformaBase):
    pass


class PlataformaResponse(PlataformaBase):
    id: int

    class Config:
        from_attributes = True


class PlataformaUpdate(BaseModel):
    nombre: Optional[str] = None
    fabricante: Optional[str] = None
    anio_lanzamiento: Optional[int] = None


# --- ESQUEMAS DE JUEGOS (ENTIDAD DEPENDIENTE) ---
class JuegoBase(BaseModel):
    titulo: str = Field(..., min_length=1, json_schema_extra={"example": "God of War Ragnarök"})
    genero: str = Field(..., min_length=2, json_schema_extra={"example": "Acción / Aventura"})
    precio: float = Field(..., ge=0.0, json_schema_extra={"example": 69.99})
    es_multijugador: bool = Field(default=False, json_schema_extra={"example": False})
    plataforma_id: int = Field(..., gt=0, json_schema_extra={"example": 1})


class JuegoCreate(JuegoBase):
    pass


class JuegoResponse(JuegoBase):
    id: int

    class Config:
        from_attributes = True


class JuegoUpdate(BaseModel):
    titulo: Optional[str] = None
    genero: Optional[str] = None
    precio: Optional[float] = None
    es_multijugador: Optional[bool] = None
    plataforma_id: Optional[int] = None


# --- SCHEMA PARA CONSULTA COMBINADA (JOIN) ---
class PlataformaConJuegosResponse(PlataformaResponse):
    juegos: List[JuegoResponse] = []
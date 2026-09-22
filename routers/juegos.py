from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from database import obtener_conexion
import seguridad
import schemas

router = APIRouter(prefix="/juegos", tags=["Juegos"])


@router.post("/", response_model=schemas.JuegoResponse, status_code=status.HTTP_201_CREATED)
def crear_juego(juego: schemas.JuegoCreate, usuario_admin=Depends(seguridad.requerir_admin)):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM plataformas WHERE id = ?", (juego.plataforma_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la plataforma con ID {juego.plataforma_id}."
        )

    cursor.execute("""
        INSERT INTO juegos (titulo, genero, precio, es_multijugador, plataforma_id)
        VALUES (?, ?, ?, ?, ?)
    """, (juego.titulo, juego.genero, juego.precio, juego.es_multijugador, juego.plataforma_id))

    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {**juego.model_dump(), "id": nuevo_id}


@router.get("/", response_model=List[schemas.JuegoResponse])
def listar_juegos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM juegos")
    juegos = cursor.fetchall()
    conn.close()

    return [dict(j) for j in juegos]


@router.get("/{juego_id}", response_model=schemas.JuegoResponse)
def obtener_juego(juego_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM juegos WHERE id = ?", (juego_id,))
    juego = cursor.fetchone()
    conn.close()

    if not juego:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Juego con ID {juego_id} no encontrado"
        )
    return dict(juego)


@router.put("/{juego_id}", response_model=schemas.JuegoResponse)
def actualizar_juego(
    juego_id: int,
    datos: schemas.JuegoUpdate,
    usuario_admin=Depends(seguridad.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM juegos WHERE id = ?", (juego_id,))
    existente = cursor.fetchone()

    if not existente:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Juego con ID {juego_id} no encontrado"
        )

    dict_ex = dict(existente)
    titulo = datos.titulo if datos.titulo is not None else dict_ex["titulo"]
    genero = datos.genero if datos.genero is not None else dict_ex["genero"]
    precio = datos.precio if datos.precio is not None else dict_ex["precio"]
    multijugador = datos.es_multijugador if datos.es_multijugador is not None else dict_ex["es_multijugador"]
    plataforma_id = datos.plataforma_id if datos.plataforma_id is not None else dict_ex["plataforma_id"]

    cursor.execute("SELECT id FROM plataformas WHERE id = ?", (plataforma_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La plataforma con ID {plataforma_id} no existe."
        )

    cursor.execute("""
        UPDATE juegos SET titulo = ?, genero = ?, precio = ?, es_multijugador = ?, plataforma_id = ?
        WHERE id = ?
    """, (titulo, genero, precio, multijugador, plataforma_id, juego_id))

    conn.commit()
    conn.close()

    return {
        "id": juego_id,
        "titulo": titulo,
        "genero": genero,
        "precio": precio,
        "es_multijugador": multijugador,
        "plataforma_id": plataforma_id
    }


@router.delete("/{juego_id}", status_code=status.HTTP_200_OK)
def eliminar_juego(juego_id: int, usuario_admin=Depends(seguridad.requerir_admin)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM juegos WHERE id = ?", (juego_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Juego con ID {juego_id} no encontrado"
        )

    cursor.execute("DELETE FROM juegos WHERE id = ?", (juego_id,))
    conn.commit()
    conn.close()

    return {"detail": f"Juego con ID {juego_id} eliminado exitosamente."}
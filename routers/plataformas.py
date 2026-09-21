from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from database import obtener_conexion
import seguridad
import schemas

router = APIRouter(prefix="/plataformas", tags=["Plataformas"])


@router.post("/", response_model=schemas.PlataformaResponse, status_code=status.HTTP_201_CREATED)
def crear_plataforma(plataforma: schemas.PlataformaBase, usuario=Depends(seguridad.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO plataformas (nombre, fabricante, anio_lanzamiento) VALUES (?, ?, ?)",
        (plataforma.nombre, plataforma.fabricante, plataforma.anio_lanzamiento)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {**plataforma.dict(), "id": nuevo_id}


@router.get("/", response_model=List[schemas.PlataformaResponse])
def listar_plataformas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plataformas")
    filas = cursor.fetchall()
    conn.close()

    return [dict(f) for f in filas]


@router.get("/{plataforma_id}", response_model=schemas.PlataformaResponse)
def obtener_plataforma(plataforma_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plataformas WHERE id = ?", (plataforma_id,))
    plataforma = cursor.fetchone()
    conn.close()

    if not plataforma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plataforma con ID {plataforma_id} no encontrada"
        )
    return dict(plataforma)


@router.put("/{plataforma_id}", response_model=schemas.PlataformaResponse)
def actualizar_plataforma(
    plataforma_id: int,
    datos: schemas.PlataformaUpdate,
    usuario=Depends(seguridad.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plataformas WHERE id = ?", (plataforma_id,))
    existente = cursor.fetchone()

    if not existente:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plataforma con ID {plataforma_id} no encontrada"
        )

    dict_ex = dict(existente)
    nombre = datos.nombre if datos.nombre is not None else dict_ex["nombre"]
    fabricante = datos.fabricante if datos.fabricante is not None else dict_ex["fabricante"]
    anio = datos.anio_lanzamiento if datos.anio_lanzamiento is not None else dict_ex["anio_lanzamiento"]

    cursor.execute(
        "UPDATE plataformas SET nombre = ?, fabricante = ?, anio_lanzamiento = ? WHERE id = ?",
        (nombre, fabricante, anio, plataforma_id)
    )
    conn.commit()
    conn.close()

    return {"id": plataforma_id, "nombre": nombre, "fabricante": fabricante, "anio_lanzamiento": anio}


@router.delete("/{plataforma_id}", status_code=status.HTTP_200_OK)
def eliminar_plataforma(plataforma_id: int, usuario_admin=Depends(seguridad.requerir_admin)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plataformas WHERE id = ?", (plataforma_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plataforma con ID {plataforma_id} no encontrada"
        )

    cursor.execute("DELETE FROM plataformas WHERE id = ?", (plataforma_id,))
    conn.commit()
    conn.close()

    return {"mensaje": f"Plataforma {plataforma_id} y sus juegos asociados eliminados."}


# Consulta Combinada con JOIN 
@router.get("/{plataforma_id}/juegos")
def obtener_juegos_por_plataforma(plataforma_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM plataformas WHERE id = ?", (plataforma_id,))
    plataforma = cursor.fetchone()

    if not plataforma:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plataforma con ID {plataforma_id} no encontrada"
        )

    cursor.execute("""
        SELECT j.id AS juego_id, j.titulo, j.genero, j.precio, j.es_multijugador,
               p.nombre AS plataforma_nombre, p.fabricante
        FROM juegos j
        INNER JOIN plataformas p ON j.plataforma_id = p.id
        WHERE p.id = ?
    """, (plataforma_id,))

    juegos = cursor.fetchall()
    conn.close()

    return {
        "plataforma_id": plataforma_id,
        "plataforma": plataforma["nombre"],
        "total_juegos": len(juegos),
        "juegos": [dict(j) for j in juegos]
    }
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
# REMUEVE la línea "from database import obtener_conexion" de aquí arriba

SECRET_KEY = "clave-super-secreta-de-mas-de-32-caracteres-cambieme"
ALGORITMO = "HS256"
MINUTOS_EXPIRACION = 30


def hashear_password(password: str) -> str:
    hasheado = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hasheado.decode('utf-8')


def verificar_password(plano: str, hasheado: str) -> bool:
    return bcrypt.checkpw(plano.encode('utf-8'), hasheado.encode('utf-8'))


def buscar_usuario(username: str):
    # IMPORTACIÓN LOCAL PARA EVITAR IMPORTACIÓN CIRCULAR
    from database import obtener_conexion
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None


def crear_token(username: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACION)
    return jwt.encode({"sub": username, "exp": expira}, SECRET_KEY, algorithm=ALGORITMO)


oauth2_esquema = OAuth2PasswordBearer(tokenUrl="auth/login")


def obtener_usuario_actual(token: str = Depends(oauth2_esquema)):
    error = HTTPException(
        status_code=401,
        detail="Token invalido",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        username = datos.get("sub")
        if username is None:
            raise error
    except jwt.PyJWTError:
        raise error

    usuario = buscar_usuario(username)
    if usuario is None:
        raise error
    return usuario


def requerir_admin(usuario: dict = Depends(obtener_usuario_actual)):
    if usuario.get("rol") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Requiere rol de administrador"
        )
    return usuario
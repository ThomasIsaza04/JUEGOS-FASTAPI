from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import seguridad
import schemas

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=schemas.TokenSchema)
def login(datos: OAuth2PasswordRequestForm = Depends()):
    usuario = seguridad.buscar_usuario(datos.username)

    if usuario is None or not seguridad.verificar_password(datos.password, usuario["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    token = seguridad.crear_token(usuario["username"])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/yo")
def quien_soy(usuario: dict = Depends(seguridad.obtener_usuario_actual)):
    return {"username": usuario["username"], "rol": usuario["rol"]}
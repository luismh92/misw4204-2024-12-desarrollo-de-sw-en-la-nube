from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/api/auth",
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.post("/signup",  tags=["auth"])
def auth_signup():
    """ Permite crear una cuenta con los campos para nombre de usuario, correo electrónico y
        contraseña. El nombre y el correo electrónico deben ser únicos en la plataforma,
        mientras que la contraseña debe seguir unos lineamientos mínimos de seguridad.
        Adicionalmente, la clave debe ser solicitada dos veces para que el usuario confirme que
        la ingresa de forma correcta. """
    return {"message": "/auth/signup"}


@router.get("/login",  tags=["auth"])
def auth_login():
    """ Permite recuperar el token de autorización para consumir los recursos del API
        suministrando el nombre de usuario y la contraseña de una cuenta previamente registrada. """
    return {"message": "/auth/login"}

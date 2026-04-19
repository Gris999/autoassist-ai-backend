from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.schemas import (
    LoginRequest,
    RegistroClienteRequest,
    RegistroClienteResponse,
    RegistroTallerRequest,
    RegistroTallerResponse,
    TokenResponse,
)
from app.modules.autenticacion_seguridad.service import (
    login_service,
    register_cliente_service,
    register_taller_service,
)

router = APIRouter(prefix="/auth", tags=["Autenticación y Seguridad"])


@router.post(
    "/register/cliente",
    response_model=RegistroClienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_cliente(
    payload: RegistroClienteRequest,
    db: Session = Depends(get_db),
):
    try:
        return register_cliente_service(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/register/taller",
    response_model=RegistroTallerResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_taller(
    payload: RegistroTallerRequest,
    db: Session = Depends(get_db),
):
    try:
        return register_taller_service(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return login_service(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
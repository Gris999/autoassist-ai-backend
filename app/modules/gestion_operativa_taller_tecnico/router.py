from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.gestion_operativa_taller_tecnico.schemas import (
    ActualizarDisponibilidadTallerRequest,
    DisponibilidadTallerResponse,
    TallerAuxilioCreateRequest,
    TallerAuxilioResponse,
    TallerAuxilioUpdateRequest,
    TallerInfoResponse,
)
from app.modules.gestion_operativa_taller_tecnico.service import (
    actualizar_disponibilidad_taller_service,
    deshabilitar_servicio_auxilio_service,
    listar_servicios_auxilio_service,
    obtener_disponibilidad_taller_service,
    obtener_informacion_taller_service,
    obtener_talleres_disponibles_service,
    registrar_servicio_auxilio_service,
    actualizar_servicio_auxilio_service,
)

router = APIRouter(prefix="/operativo/taller", tags=["Gestión Operativa Taller"])


@router.get(
    "/me",
    response_model=TallerInfoResponse,
    status_code=status.HTTP_200_OK,
)
def obtener_informacion_taller(
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return obtener_informacion_taller_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/disponibilidad",
    response_model=DisponibilidadTallerResponse,
    status_code=status.HTTP_200_OK,
)
def obtener_disponibilidad(
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return obtener_disponibilidad_taller_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/disponibilidad",
    response_model=DisponibilidadTallerResponse,
    status_code=status.HTTP_200_OK,
)
def actualizar_disponibilidad(
    payload: ActualizarDisponibilidadTallerRequest,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return actualizar_disponibilidad_taller_service(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/servicios-auxilio",
    response_model=list[TallerAuxilioResponse],
    status_code=status.HTTP_200_OK,
)
def listar_servicios_auxilio(
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return listar_servicios_auxilio_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/servicios-auxilio",
    response_model=TallerAuxilioResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_servicio_auxilio(
    payload: TallerAuxilioCreateRequest,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return registrar_servicio_auxilio_service(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/servicios-auxilio/{id_taller_auxilio}",
    response_model=TallerAuxilioResponse,
    status_code=status.HTTP_200_OK,
)
def actualizar_servicio_auxilio(
    id_taller_auxilio: int,
    payload: TallerAuxilioUpdateRequest,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return actualizar_servicio_auxilio_service(db, current_user, id_taller_auxilio, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/servicios-auxilio/{id_taller_auxilio}/deshabilitar",
    response_model=TallerAuxilioResponse,
    status_code=status.HTTP_200_OK,
)
def deshabilitar_servicio_auxilio(
    id_taller_auxilio: int,
    current_user: Usuario = Depends(require_roles("TALLER")),
    db: Session = Depends(get_db),
):
    try:
        return deshabilitar_servicio_auxilio_service(db, current_user, id_taller_auxilio)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/disponibles",
    response_model=list[TallerInfoResponse],
    status_code=status.HTTP_200_OK,
)
def listar_talleres_disponibles(
    db: Session = Depends(get_db),
):
    try:
        return obtener_talleres_disponibles_service(db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

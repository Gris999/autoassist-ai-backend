from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.autenticacion_seguridad.models import Usuario
from app.modules.autenticacion_seguridad.permissions import require_roles
from app.modules.gestion_incidentes_atencion.schemas import (
    IncidenteCreateRequest,
    IncidenteResponse,
)
from app.modules.gestion_incidentes_atencion.service import (
    get_mis_incidentes_service,
    report_incidente_service,
)

router = APIRouter(prefix="/incidentes", tags=["Gestión Incidentes y Atención"])


@router.post(
    "",
    response_model=IncidenteResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_incidente(
    payload: IncidenteCreateRequest,
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return report_incidente_service(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/mis",
    response_model=list[IncidenteResponse],
    status_code=status.HTTP_200_OK,
)
def get_mis_incidentes(
    current_user: Usuario = Depends(require_roles("CLIENTE")),
    db: Session = Depends(get_db),
):
    try:
        return get_mis_incidentes_service(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
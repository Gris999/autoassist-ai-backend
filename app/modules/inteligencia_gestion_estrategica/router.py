from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.inteligencia_gestion_estrategica.schemas import (
    AnalisisIncidenteManualRequest,
    AnalisisIncidenteResponse,
)
from app.modules.inteligencia_gestion_estrategica.service import (
    IncidentNotFoundError,
    analizar_incidente_manual_service,
    analizar_incidente_por_id_service,
)

router = APIRouter(
    prefix="/inteligencia",
    tags=["Inteligencia y Gesti\u00f3n Estrat\u00e9gica"],
)


@router.post(
    "/incidentes/analizar",
    response_model=AnalisisIncidenteResponse,
    status_code=status.HTTP_200_OK,
)
def analizar_incidente_manual(
    payload: AnalisisIncidenteManualRequest,
):
    try:
        return analizar_incidente_manual_service(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrio un error inesperado durante el analisis del incidente.",
        ) from exc


@router.post(
    "/incidentes/{id_incidente}/analizar",
    response_model=AnalisisIncidenteResponse,
    status_code=status.HTTP_200_OK,
)
def analizar_incidente_por_id(
    id_incidente: int,
    db: Session = Depends(get_db),
):
    try:
        return analizar_incidente_por_id_service(db, id_incidente)
    except IncidentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrio un error inesperado durante el analisis o guardado del incidente.",
        ) from exc

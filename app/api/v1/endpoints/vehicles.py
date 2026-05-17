from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin, require_authenticated
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from app.services.vehicle_service import VehicleService


router = APIRouter(prefix="/vehicles", tags=["Vehículos"])


@router.get("", response_model=ApiResponse[list[VehicleRead]])
async def list_vehicles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    _: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    vehicles = await VehicleService(db).list_vehicles(skip=skip, limit=limit)
    return success_response(message="Vehículos obtenidos correctamente", data=vehicles)


@router.get("/{vehicle_id}", response_model=ApiResponse[VehicleRead])
async def get_vehicle(
    vehicle_id: int,
    _: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    vehicle = await VehicleService(db).get_vehicle(vehicle_id)
    return success_response(message="Vehículo obtenido correctamente", data=vehicle)


@router.post("", response_model=ApiResponse[VehicleRead], status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    vehicle = await VehicleService(db).create_vehicle(vehicle_in)
    return success_response(message="Vehículo creado correctamente", data=vehicle)


@router.patch("/{vehicle_id}", response_model=ApiResponse[VehicleRead])
async def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    vehicle = await VehicleService(db).update_vehicle(vehicle_id, vehicle_in)
    return success_response(message="Vehículo actualizado correctamente", data=vehicle)


@router.delete("/{vehicle_id}", response_model=ApiResponse[None])
async def delete_vehicle(
    vehicle_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await VehicleService(db).delete_vehicle(vehicle_id)
    return success_response(message="Vehículo eliminado correctamente")

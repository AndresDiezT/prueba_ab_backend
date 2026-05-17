from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, db: AsyncSession) -> None:
        self.vehicle_repository = VehicleRepository(db)

    async def list_vehicles(self, skip: int = 0, limit: int = 100) -> list[Vehicle]:
        return await self.vehicle_repository.list(skip=skip, limit=limit)

    async def get_vehicle(self, vehicle_id: int) -> Vehicle:
        vehicle = await self.vehicle_repository.get(vehicle_id)
        if not vehicle:
            raise NotFoundException("Vehículo no encontrado")
        return vehicle

    async def create_vehicle(self, vehicle_in: VehicleCreate) -> Vehicle:
        return await self.vehicle_repository.create(vehicle_in)

    async def update_vehicle(self, vehicle_id: int, vehicle_in: VehicleUpdate) -> Vehicle:
        vehicle = await self.get_vehicle(vehicle_id)
        return await self.vehicle_repository.update(vehicle, vehicle_in)

    async def delete_vehicle(self, vehicle_id: int) -> None:
        vehicle = await self.get_vehicle(vehicle_id)
        await self.vehicle_repository.delete(vehicle)

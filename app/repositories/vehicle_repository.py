from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(self, skip: int = 0, limit: int = 100) -> list[Vehicle]:
        result = await self.db.execute(select(Vehicle).order_by(Vehicle.id.desc()).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get(self, vehicle_id: int) -> Vehicle | None:
        return await self.db.get(Vehicle, vehicle_id)

    async def create(self, vehicle_in: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_in.model_dump())
        self.db.add(vehicle)
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle

    async def update(self, vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle:
        update_data = vehicle_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle

    async def delete(self, vehicle: Vehicle) -> None:
        await self.db.delete(vehicle)
        await self.db.commit()

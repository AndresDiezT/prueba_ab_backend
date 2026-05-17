from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    brand: str = Field(min_length=1, max_length=80, examples=["Toyota"])
    arrival_location: str = Field(min_length=1, max_length=120, examples=["Bogota"])
    applicant_name: str = Field(min_length=1, max_length=120, examples=["Laura Gomez"])


class VehicleCreate(VehicleBase):
    """Datos requeridos para crear un vehículo."""


class VehicleUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=80)
    arrival_location: str | None = Field(default=None, min_length=1, max_length=120)
    applicant_name: str | None = Field(default=None, min_length=1, max_length=120)


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

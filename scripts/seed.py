import asyncio

from sqlalchemy import func, select

from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.vehicle import Vehicle


async def seed() -> None:
    async with SessionLocal() as db:
        # Credenciales demo intencionales para facilitar la revisión manual de la prueba.
        users = [
            {"username": "admin", "password": "Admin12345", "role": UserRole.ADMIN},
            {"username": "viewer", "password": "Viewer12345", "role": UserRole.VIEWER},
        ]

        for user_data in users:
            result = await db.execute(select(User).where(User.username == user_data["username"]))
            user = result.scalar_one_or_none()
            if user:
                user.hashed_password = hash_password(user_data["password"])
                user.role = user_data["role"]
                user.is_active = True
            else:
                db.add(
                    User(
                        username=user_data["username"],
                        hashed_password=hash_password(user_data["password"]),
                        role=user_data["role"],
                    )
                )

        count_result = await db.execute(select(func.count()).select_from(Vehicle))
        vehicle_count = count_result.scalar_one()
        if vehicle_count == 0:
            db.add_all(
                [
                    Vehicle(brand="Toyota", arrival_location="Bogota", applicant_name="Laura Gomez"),
                    Vehicle(brand="Mazda", arrival_location="Medellin", applicant_name="Carlos Perez"),
                    Vehicle(brand="Renault", arrival_location="Cali", applicant_name="Andrea Ruiz"),
                ]
            )

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print("Datos iniciales cargados correctamente")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from models import Base, CoffeeMachineORM, PaymentORM, MachineModelORM
from datetime import date
from typing import Optional

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Работа с моделями кофемашин ---
async def get_all_machine_models():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MachineModelORM))
        return result.scalars().all()

async def add_machine_model(name: str, default_rent: float, full_price: float):
    async with AsyncSessionLocal() as session:
        model = MachineModelORM(name=name, default_rent=default_rent, full_price=full_price)
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

async def delete_machine_model(model_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(MachineModelORM).where(MachineModelORM.id == model_id))
        await session.commit()

# CRUD-функции
async def add_coffee_machine(machine_data: dict):
    async with AsyncSessionLocal() as session:
        machine = CoffeeMachineORM(**machine_data)
        session.add(machine)
        await session.commit()
        await session.refresh(machine)
        return machine

async def get_all_machines():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CoffeeMachineORM))
        return result.scalars().all()

async def add_payment(payment_data: dict):
    async with AsyncSessionLocal() as session:
        payment = PaymentORM(**payment_data)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

async def get_payments_by_machine(machine_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PaymentORM).where(PaymentORM.machine_id == machine_id))
        return result.scalars().all()

async def update_machine_payment_date(machine_id: int, new_payment_date: date):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(CoffeeMachineORM)
            .where(CoffeeMachineORM.id == machine_id)
            .values(payment_date=new_payment_date)
        )
        await session.commit()

async def update_machine_status(machine_id: int, status: str, buyout: bool = False, buyout_date: Optional[date] = None):
    async with AsyncSessionLocal() as session:
        values = {"status": status, "buyout": buyout}
        if buyout_date is not None:
            values["buyout_date"] = buyout_date
        
        await session.execute(
            update(CoffeeMachineORM)
            .where(CoffeeMachineORM.id == machine_id)
            .values(**values)
        )
        await session.commit() 
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, ARRAY, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

Base = declarative_base()

class CoffeeMachineORM(Base):
    __tablename__ = 'coffee_machines'
    id = Column(Integer, primary_key=True)
    model = Column(String(100), nullable=False)
    barcode = Column(String(100), nullable=False, unique=True)
    rent_price = Column(Float, nullable=False)
    tenant = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    deposit = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    in_1C = Column(Boolean, default=False)
    status = Column(String(20), default='active')
    buyout = Column(Boolean, default=False)
    buyout_date = Column(Date, nullable=True)
    payments = Column(ARRAY(Date), default=[])
    deal_type = Column(String(20), default='Аренда')  # Аренда или Рассрочка
    comment = Column(Text, nullable=True)
    full_price = Column(Float, nullable=True)  # Индивидуальная стоимость
    payments_rel = relationship('PaymentORM', back_populates='machine')

class PaymentORM(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('coffee_machines.id'))
    tenant = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    is_deposit = Column(Boolean, default=False)
    is_buyout = Column(Boolean, default=False)
    machine = relationship('CoffeeMachineORM', back_populates='payments_rel')

# Pydantic-схемы для валидации и передачи данных
class CoffeeMachine(BaseModel):
    id: Optional[int] = None
    model: str
    barcode: str
    rent_price: float
    tenant: str
    phone: str
    deposit: float
    payment_date: date
    in_1C: bool = False
    status: str = "active"  # active, buyout, returned, damaged, etc.
    buyout: bool = False
    buyout_date: Optional[date] = None
    payments: List[date] = Field(default_factory=list)
    deal_type: str = "Аренда"
    comment: Optional[str] = None
    full_price: Optional[float] = None

class Payment(BaseModel):
    id: Optional[int] = None
    machine_id: int
    tenant: str
    amount: float
    payment_date: date
    is_deposit: bool = False
    is_buyout: bool = False

class MachineModelORM(Base):
    __tablename__ = 'machine_models'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    default_rent = Column(Float, nullable=False)
    full_price = Column(Float, nullable=False, default=0) 
import os
import re

from datetime import datetime
from typing import Annotated

import pytest

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    MetaData,
    String,
    event,
    func,
    select,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
    selectinload,
    sessionmaker,
)
from sqlalchemy.orm import registry as Registry

from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories.sqlalchemy import SQLAlchemyModelFactory


SQLA_TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(SQLA_TEST_DIR, "fixtures")

# types
pk = Annotated[int, mapped_column(primary_key=True)]
str25 = Annotated[str, 25]
str50 = Annotated[str, 50]

registry = Registry(
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    ),
    type_annotation_map={
        int: BigInteger,
        datetime: TIMESTAMP(timezone=True),
        str25: String(25),
        str50: String(50),
    },
)


class Base(DeclarativeBase):
    __abstract__ = True

    registry = registry

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls):
        # convert ClassName to snake_case
        s = re.sub(r"([a-z0-9])([A-Z])", "\\1_\\2", cls.__name__)
        return re.sub(r"([A-Z])([A-Z][a-z])", "\\1_\\2", s).lower()


class Company(Base):
    id: Mapped[pk]

    name: Mapped[str50]

    employees: Mapped[list["Employee"]] = relationship(back_populates="company")
    managers: Mapped[list["Manager"]] = relationship(
        back_populates="company",
        primaryjoin="Company.id == Manager.company_id",
        remote_side="Manager.company_id",
        viewonly=True,
    )
    products: Mapped[list["Product"]] = relationship(back_populates="company")

    company_customers: Mapped[list["CompanyCustomer"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    customers: list["Customer"] = association_proxy(
        "company_customers",
        "customer",
        creator=lambda customer: CompanyCustomer(customer=customer),
    )


class Employee(Base):
    id: Mapped[pk]

    first_name: Mapped[str25]
    last_name: Mapped[str50]

    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    company: Mapped[Company] = relationship(back_populates="employees")

    manager_id: Mapped[int | None] = mapped_column(ForeignKey("manager.id"))
    manager: Mapped["Manager"] = relationship(
        back_populates="reports",
        foreign_keys=[manager_id],
    )

    type: Mapped[str25]
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": "type",
    }


class Manager(Employee):
    id: Mapped[pk] = mapped_column(ForeignKey("employee.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "manager",
        "inherit_condition": id == Employee.id,
    }

    reports: Mapped[list[Employee]] = relationship(
        back_populates="manager",
        primaryjoin=id == Employee.manager_id,
        remote_side=[Employee.manager_id],
    )


class Product(Base):
    id: Mapped[pk]

    name: Mapped[str50]

    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    company: Mapped[Company] = relationship(back_populates="products")


class Customer(Base):
    id: Mapped[pk]

    name: Mapped[str50]

    customer_companies: Mapped[list["CompanyCustomer"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    suppliers: list["Company"] = association_proxy(
        "customer_companies",
        "company",
        creator=lambda company: CompanyCustomer(company=company),
    )


class CompanyCustomer(Base):
    """
    Join table between Company and Customer
    """

    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), primary_key=True)
    company: Mapped[Company] = relationship(back_populates="company_customers")

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id"),
        primary_key=True,
    )
    customer: Mapped[Customer] = relationship(back_populates="customer_companies")


@pytest.fixture
def async_engine() -> AsyncEngine:
    yield create_async_engine(
        "postgresql+asyncpg://yaml:yaml@localhost:5432/yaml_test", future=True
    )


@pytest.fixture
async def async_session(async_engine) -> AsyncSession:
    connection = await async_engine.connect()
    transaction = await connection.begin()

    await connection.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async_session = async_session_factory(bind=connection)
    nested = await connection.begin_nested()

    @event.listens_for(async_session.sync_session, "after_transaction_end")
    def end_savepoint(sess, trans):
        nonlocal nested

        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    yield async_session

    await transaction.rollback()
    await connection.run_sync(Base.metadata.drop_all)
    await async_session.close()
    await connection.close()


async def test_sqlalchemy20(async_session: AsyncSession):
    def sync_loader(session):
        loader = FixturesLoader(
            factory=SQLAlchemyModelFactory(
                session=session, models=[x.class_ for x in registry.mappers]
            ),
            fixture_dirs=[FIXTURES_DIR],
        )
        loader.create_all()

    await async_session.run_sync(sync_loader)

    products = (await async_session.scalars(select(Product))).all()
    assert len(products) == 4, products

    acme = (
        await async_session.scalars(
            select(Company)
            .filter_by(name="ACME")
            .options(
                selectinload(Company.employees),
                selectinload(Company.managers),
                selectinload(Company.company_customers),
            )
        )
    ).one()
    assert len(acme.employees) == 3, acme.employees
    assert len(acme.managers) == 1, acme.managers
    manager = acme.managers[0]
    assert manager.last_name == "Man (ACME)"

    fang = (
        await async_session.scalars(
            select(Company)
            .filter_by(name="FANG")
            .options(
                selectinload(Company.employees),
                selectinload(Company.managers),
                selectinload(Company.company_customers),
            )
        )
    ).one()
    assert len(fang.employees) == 3, acme.employees
    assert len(fang.managers) == 1, fang.managers
    manager = fang.managers[0]
    assert manager.last_name == "Man (FANG)"

    customers = (await async_session.scalars(select(Customer))).all()
    assert len(customers) == 3, customers
    assert acme.customers == [customers[0], customers[2]]
    assert fang.customers == [customers[1], customers[2]]

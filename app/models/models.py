from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    sales = relationship("SaleItem", back_populates="product", cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="inventory")
    inventory_history = relationship("InventoryHistory", back_populates="inventory", cascade="all, delete-orphan")


class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    inventory = relationship("Inventory", back_populates="inventory_history")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="completed")

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sales") 
import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.models.models import (
    Category, Product, Inventory, Customer, Sale, SaleItem, InventoryHistory
)

fake = Faker()


async def clear_tables(db: AsyncSession):
    """Clear all tables before loading demo data."""
    await db.execute(delete(SaleItem))
    await db.execute(delete(Sale))
    await db.execute(delete(InventoryHistory))
    await db.execute(delete(Inventory))
    await db.execute(delete(Product))
    await db.execute(delete(Category))
    await db.execute(delete(Customer))
    await db.commit()


async def create_categories(db: AsyncSession):
    """Create product categories."""
    categories = [
        Category(name="Electronics", description="Electronic devices and accessories"),
        Category(name="Clothing", description="Apparel and fashion items"),
        Category(name="Home & Kitchen", description="Household items and appliances"),
        Category(name="Books", description="Books and publications"),
        Category(name="Toys", description="Toys and games for all ages"),
    ]
    
    db.add_all(categories)
    await db.commit()
    
    for category in categories:
        await db.refresh(category)
    
    return categories


async def create_products(db: AsyncSession, categories):
    """Create products in various categories."""
    products = []
    
    for i in range(20):
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word().capitalize()} Device",
            description=fake.paragraph(),
            price=round(random.uniform(99.99, 1999.99), 2),
            category_id=categories[0].id,
            sku=f"ELEC-{fake.unique.random_number(5)}",
            image_url=f"https://example.com/images/electronics/{i+1}.jpg"
        )
        products.append(product)
    
    for i in range(30):
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word().capitalize()} Apparel",
            description=fake.paragraph(),
            price=round(random.uniform(19.99, 199.99), 2),
            category_id=categories[1].id,
            sku=f"CLTH-{fake.unique.random_number(5)}",
            image_url=f"https://example.com/images/clothing/{i+1}.jpg"
        )
        products.append(product)
    
    for i in range(25):
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word().capitalize()} Home Item",
            description=fake.paragraph(),
            price=round(random.uniform(29.99, 599.99), 2),
            category_id=categories[2].id,
            sku=f"HOME-{fake.unique.random_number(5)}",
            image_url=f"https://example.com/images/home/{i+1}.jpg"
        )
        products.append(product)
    
    for i in range(40):
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word().capitalize()} Book",
            description=fake.paragraph(),
            price=round(random.uniform(9.99, 49.99), 2),
            category_id=categories[3].id,
            sku=f"BOOK-{fake.unique.random_number(5)}",
            image_url=f"https://example.com/images/books/{i+1}.jpg"
        )
        products.append(product)
    
    for i in range(15):
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word().capitalize()} Toy",
            description=fake.paragraph(),
            price=round(random.uniform(14.99, 99.99), 2),
            category_id=categories[4].id,
            sku=f"TOY-{fake.unique.random_number(5)}",
            image_url=f"https://example.com/images/toys/{i+1}.jpg"
        )
        products.append(product)
    
    db.add_all(products)
    await db.commit()
    
    for product in products:
        await db.refresh(product)
    
    return products


async def create_inventory(db: AsyncSession, products):
    """Create inventory for all products."""
    inventory_items = []
    
    for product in products:
        quantity = random.randint(5, 200)
        inventory = Inventory(
            product_id=product.id,
            quantity=quantity
        )
        inventory_items.append(inventory)
    
    db.add_all(inventory_items)
    await db.commit()
    
    for item in inventory_items:
        await db.refresh(item)
    
    return inventory_items


async def create_customers(db: AsyncSession, count=50):
    """Create customer records."""
    customers = []
    
    for _ in range(count):
        customer = Customer(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number()
        )
        customers.append(customer)
    
    db.add_all(customers)
    await db.commit()
    
    for customer in customers:
        await db.refresh(customer)
    
    return customers


async def create_sales(db: AsyncSession, products, customers, count=200):
    """Create sales records with items."""
    sales = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for _ in range(count):
        sale_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        
        sale = Sale(
            customer_id=random.choice(customers).id if random.random() > 0.2 else None,
            sale_date=sale_date,
            payment_method=random.choice(["Credit Card", "PayPal", "Bank Transfer", "Cash"]),
            status="completed",
            total_amount=0
        )
        
        db.add(sale)
        await db.flush()
        
        items_count = random.randint(1, 5)
        selected_products = random.sample(products, items_count)
        
        total_amount = 0
        for product in selected_products:
            quantity = random.randint(1, 3)
            subtotal = product.price * quantity
            total_amount += subtotal
            
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                subtotal=subtotal
            )
            db.add(sale_item)
            
            result = await db.execute(
                select(Inventory).where(Inventory.product_id == product.id)
            )
            inventory = result.scalars().first()
            
            if inventory:
                previous_quantity = inventory.quantity
                inventory.quantity = max(0, previous_quantity - quantity)
                
                history_entry = InventoryHistory(
                    inventory_id=inventory.id,
                    quantity_change=-quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=inventory.quantity,
                    reason=f"Sale ID: {sale.id}"
                )
                db.add(history_entry)
        
        sale.total_amount = total_amount
        sales.append(sale)
    
    await db.commit()
    return sales


async def load_demo_data():
    """Main function to load all demo data."""
    async with AsyncSessionLocal() as db:
        print("Clearing existing data...")
        await clear_tables(db)
        
        print("Creating categories...")
        categories = await create_categories(db)
        
        print("Creating products...")
        products = await create_products(db, categories)
        
        print("Creating inventory...")
        inventory = await create_inventory(db, products)
        
        print("Creating customers...")
        customers = await create_customers(db)
        
        print("Creating sales...")
        sales = await create_sales(db, products, customers)
        
        print(f"Demo data loaded successfully!")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(products)} products")
        print(f"Created {len(inventory)} inventory items")
        print(f"Created {len(customers)} customers")
        print(f"Created {len(sales)} sales")


if __name__ == "__main__":
    asyncio.run(load_demo_data()) 
# E-commerce Admin API

A FastAPI-based backend API for an e-commerce admin dashboard. This API provides insights into sales, revenue, and inventory management.

## Features

- **Sales Status**: Analyze and filter sales data by various parameters
- **Revenue Analytics**: Track revenue by day, week, month, and year
- **Inventory Management**: Monitor stock levels and receive low stock alerts
- **Product Registration**: Add new products to the inventory

## Getting Started

### Prerequisites

- Python 3.9+
- SQLite (included with Python, no separate installation needed)

### Installation & Setup


1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .  # Install the package in development mode
```

3. Run database migrations:
```bash
# Create the initial database
alembic upgrade head
```

4. Load demo data:
```bash
python -m app.scripts.load_demo_data
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

6. Access the API documentation:
```
http://127.0.0.1:8000/docs
```

## Making Changes to the Database

If you need to modify the database schema:

1. Update models in `app/models/models.py`
2. Generate a migration:
```bash
alembic revision --autogenerate -m "description of your changes"
```
3. Apply the migration:
```bash
alembic upgrade head
```

## API Endpoints

### Sales
- `GET /api/sales` - List all sales with filtering options
- `GET /api/sales/{sale_id}` - Get details of a specific sale

### Revenue
- `GET /api/revenue/daily` - Daily revenue statistics
- `GET /api/revenue/weekly` - Weekly revenue statistics
- `GET /api/revenue/monthly` - Monthly revenue statistics
- `GET /api/revenue/annual` - Annual revenue statistics
- `GET /api/revenue/compare` - Compare revenue across periods

### Inventory
- `GET /api/inventory` - Current inventory status
- `GET /api/inventory/low-stock` - Products with low stock
- `PUT /api/inventory/{product_id}` - Update inventory level

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Register a new product
- `GET /api/products/{product_id}` - Get details of a specific product
- `PUT /api/products/{product_id}` - Update product details
- `DELETE /api/products/{product_id}` - Delete a product

## Database Schema

The database consists of the following tables:

1. **products** - Stores product information
2. **inventory** - Tracks inventory levels and changes
3. **sales** - Records all sales transactions
4. **categories** - Product categories
5. **customers** - Customer data

Check the [database documentation](docs/database.md) for detailed schema information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
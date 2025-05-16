# Database Schema Documentation

This document provides an overview of the database schema used in the E-commerce Admin API.

## Tables

### categories

Stores product categories.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Category name (unique) |
| description | Text | Category description |

### products

Stores product information.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Product name |
| description | Text | Product description |
| price | Float | Product price |
| category_id | Integer | Foreign key to categories |
| sku | String | Stock keeping unit (unique) |
| image_url | String | URL to product image |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### inventory

Tracks current inventory levels.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| product_id | Integer | Foreign key to products |
| quantity | Integer | Current stock quantity |
| last_updated | DateTime | Last update timestamp |

### inventory_history

Tracks all changes to inventory levels.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| inventory_id | Integer | Foreign key to inventory |
| quantity_change | Integer | Change amount (positive or negative) |
| previous_quantity | Integer | Quantity before change |
| new_quantity | Integer | Quantity after change |
| reason | String | Reason for change |
| timestamp | DateTime | When the change occurred |

### customers

Stores customer information.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Customer name |
| email | String | Customer email (unique) |
| phone | String | Customer phone number |
| created_at | DateTime | Account creation timestamp |

### sales

Records of sales transactions.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| customer_id | Integer | Foreign key to customers (nullable) |
| total_amount | Float | Total sale amount |
| sale_date | DateTime | When the sale occurred |
| payment_method | String | Method of payment |
| status | String | Sale status (completed, cancelled, etc.) |

### sale_items

Line items for each sale.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| sale_id | Integer | Foreign key to sales |
| product_id | Integer | Foreign key to products |
| quantity | Integer | Quantity sold |
| unit_price | Float | Price per unit |
| subtotal | Float | Total for this item (quantity * unit_price) |

## Relationships

- A **Category** has many **Products**
- A **Product** belongs to one **Category**
- A **Product** has one **Inventory** record
- An **Inventory** record has many **InventoryHistory** records
- A **Customer** has many **Sales**
- A **Sale** belongs to one **Customer** (optional)
- A **Sale** has many **SaleItems**
- A **SaleItem** belongs to one **Sale** and one **Product**

## Indexes

The following columns are indexed for better query performance:

- categories.id (primary key)
- categories.name (unique index)
- products.id (primary key)
- products.name (index)
- products.category_id (foreign key index)
- products.sku (unique index)
- inventory.id (primary key)
- inventory.product_id (unique foreign key index)
- inventory_history.id (primary key)
- inventory_history.inventory_id (foreign key index)
- customers.id (primary key)
- customers.email (unique index)
- sales.id (primary key)
- sales.customer_id (foreign key index)
- sales.sale_date (index for date filtering)
- sale_items.id (primary key)
- sale_items.sale_id (foreign key index)
- sale_items.product_id (foreign key index) 
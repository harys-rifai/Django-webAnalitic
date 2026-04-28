# Sales Dashboard - Django Web Analytics

A Django-based web analytics dashboard connected to an existing PostgreSQL database (`moao_db`) originally used by a Laravel application.

## Features

### Authentication
- **Login Page**: Custom login using existing Laravel users table
- **Bcrypt Support**: Compatible with Laravel's bcrypt hashed passwords
- **Session Management**: Django session-based authentication
- **Logout**: Secure session cleanup

### Dashboard Analytics

#### Summary Statistics
- Total active users
- Total purchase requests
- Total purchase orders
- Total assets
- Total PO value (Rp)
- Monthly material receipts

#### Visual Analytics
- **Purchase Requests by Status**: Doughnut chart showing PR distribution
- **Assets by Condition**: Bar chart displaying asset conditions

#### Data Tables
- **Top Departments**: Top 5 departments by purchase request count
- **Recent Purchase Requests**: Last 10 PRs with status badges

### Database Models

Connected to existing `moao_db` tables (read-only, `managed = False`):
- `Companies` - Company management
- `Departments` - Department structure
- `Users` - User accounts (Laravel compatible)
- `Distributors` - Vendor/supplier data
- `PurchaseRequests` - PR tracking
- `PurchaseOrders` - PO management
- `MaterialReceipts` - Goods receipt records
- `Assets` - Asset tracking
- `Stocks` - Inventory management

## Technology Stack

- **Backend**: Django 4.2.30
- **Database**: PostgreSQL (existing `moao_db`)
- **Charts**: Chart.js
- **Password Hashing**: bcrypt (compatible with Laravel)
- **Python**: 3.9.6

## Installation

1. Install dependencies:
```bash
pip3 install django psycopg2-binary bcrypt
```

2. Configure database in `sales_dashboard/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moao_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Run migrations (creates Django core tables):
```bash
python3 manage.py migrate
```

4. Start the server:
```bash
./run.sh
```
Or manually:
```bash
python3 manage.py runserver 0.0.0.0:8000
```

## Usage

1. Access the dashboard at **http://127.0.0.1:8000/**
2. Login with existing Laravel app credentials (email + password)
3. View analytics dashboard at **/dashboard/**

## Project Structure

```
sales_dashboard/
├── finance/
│   ├── models.py          # Database models (existing tables)
│   ├── views.py           # Login, logout, dashboard views
│   ├── urls.py            # Finance app URLs
│   └── templates/finance/
│       ├── login.html     # Login page
│       └── dashboard.html # Analytics dashboard
├── sales_dashboard/
│   ├── settings.py        # Django configuration
│   └── urls.py            # Main URL routing
├── run.sh                 # Server startup script
└── README.md
```

## Notes

- Models are set to `managed = False` - Django won't modify existing tables
- Password verification supports Laravel's `$2y$` bcrypt format
- The app reads from an existing Laravel database without migration conflicts
- Timezone warnings for naive datetimes can be ignored or fixed by updating model fields

## License

MIT

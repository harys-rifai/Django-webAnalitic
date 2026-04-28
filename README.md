# Sales Dashboard - Django Web Analytics

A Django-based web analytics dashboard connected to an existing PostgreSQL database (`moao_db`) originally used by a Laravel application. Features role-based analytics for Admin, CEO, and regular Users.

## Features

### Authentication
- **Login Page**: Custom login using existing Laravel users table
- **Bcrypt Support**: Compatible with Laravel's bcrypt hashed passwords
- **Session Management**: Django session-based authentication
- **Role-Based Access**: Admin, CEO, and User roles from existing `role_user` table
- **Logout**: Secure session cleanup

### Role-Based Dashboard Analytics

#### Admin & CEO View (Full Access)
- **Summary Statistics**: Active users, total PRs, POs, assets, stock items, low stock alerts
- **Interactive Stat Cards**: Small, clickable cards with hover effects and click-to-detail
- **Financial Analytics**: Total PO value, monthly receipts
- **Visual Charts**:
  - Purchase Requests by Status (Doughnut chart)
  - Assets by Condition (Bar chart)
- **Data Tables**:
  - Top 5 departments by purchase requests
  - Recent stock items with low-stock alerts
  - Recent purchase requests

#### Regular User View (Personal Data)
- **Personal Statistics**: My PRs, pending approvals, approved requests, personal inventory count
- **Interactive Stat Cards**: Compact, animated cards with hover effects
- **Financial**: My total request value
- **Personal Data Tables**:
  - My recent purchase requests with status badges
  - My inventory items with stock status

### Stock & Inventory Management
- **Stock Tracking**: View all stock items (Admin/CEO) or personal items (User)
- **Low Stock Alerts**: Automatic detection and highlighting of low-stock items
- **Stock Details**: SKU, name, quantity, unit price, location, condition

### Version & System Info
- **Login Page Footer**: Displays Python version, database name, and app version
- **Dashboard Footer**: Shows Python version, database (`moao_db`), and app version from `app_versions` table
- **App Version**: Dynamically fetched from database `app_versions` table

### Database Models

Connected to existing `moao_db` tables (read-only, `managed = False`):
- `Companies` - Company management
- `Departments` - Department structure
- `Users` - User accounts (Laravel compatible)
- `Roles` & `RoleUser` - User role assignments
- `AppVersions` - Application version tracking
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
- **Python**: 3.9.6+

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
3. Dashboard analytics are automatically filtered by user role:
   - **Admin/CEO**: See all company data and analytics
   - **User/Requestor**: See only personal data and requests
4. View Python version, database info, and app version in page footers

## Pages

1. **`/login/`** (or `/`) - Login page with system info footer
2. **`/dashboard/`** - Role-based analytics dashboard
3. **`/logout/`** - Logout (redirects to login)
4. **`/admin/`** - Django admin (not configured yet)

## Project Structure

```
sales_dashboard/
├── finance/
│   ├── models.py          # Database models (existing tables)
│   ├── views.py           # Login, logout, role-based dashboard views
│   ├── urls.py            # Finance app URLs
│   └── templates/finance/
│       ├── login.html     # Login page with version info
│       └── dashboard.html # Role-based analytics dashboard
├── sales_dashboard/
│   ├── settings.py        # Django configuration
│   └── urls.py            # Main URL routing
├── run.sh                 # Server startup script
└── README.md
```

## Role Detection

User roles are determined by querying the `role_user` table joined with `roles` table:
- Roles from `roles` table (e.g., 'admin', 'ceo', 'User', 'requestor')
- Stored in session upon login
- Dashboard content adapts based on role

## Notes

- Models are set to `managed = False` - Django won't modify existing tables
- Password verification supports Laravel's `$2y$` bcrypt format
- The app reads from an existing Laravel database without migration conflicts
- App version is dynamically fetched from `app_versions` table (falls back to '1.0.0')
- Timezone warnings for naive datetimes can be ignored or fixed by updating model fields

## License

MIT

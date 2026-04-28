# Data Analytic - Django Web Analytics

A Django-based web analytics dashboard connected to an existing PostgreSQL database (`moao_db`) originally used by a Laravel application. Features role-based analytics for Admin, CEO, and regular Users with interactive charts and colored stat cards.

![Dashboard Preview](https://via.placeholder.com/800x400/667eea/ffffff?text=Data+Analytic+Dashboard)

## Features

### Authentication
- **Login Page**: Custom login using existing Laravel users table
- **Bcrypt Support**: Compatible with Laravel's bcrypt hashed passwords
- **Session Management**: Django session-based authentication
- **Role-Based Access**: Admin, CEO, Manager, User, and Requestor roles from existing `role_user` table
- **Logout**: Secure session cleanup

### Header & Title
- **Title**: "Data Analytic" with 📊 icon
- **Role Badge**: Shows current user role in header
- **User Info**: Displays logged-in user name

### Role-Based Dashboard Analytics

#### Admin & CEO View (Full Access - All Data)
![Admin Dashboard](https://via.placeholder.com/800x600/667eea/ffffff?text=Admin+Dashboard)

**Interactive Colored Stat Cards:**
- 🔵 **Active Users** (Blue)
- 🟢 **Purchase Requests** (Green)
- 🟣 **Purchase Orders** (Purple)
- 🟠 **Total Assets** (Orange)
- 🔵 **PO Value Total** (Teal)
- 🔴 **Monthly Receipts** (Red)
- 🔵 **Stock Items** (Blue)
- 🔴 **Low Stock Items** (Red)

**Charts & Graphs:**
- 📊 Purchase Requests by Status (Doughnut chart)
- 📊 Assets by Condition (Bar chart)
- 📈 Monthly PR Trends (Line chart)
- 📊 Monthly PO Value (Bar chart)
- 📈 Revenue vs Expense Chart

**Data Tables:**
- Top 5 departments by purchase requests
- Recent stock items with low-stock alerts
- Recent purchase requests

**Export:** Full data export to CSV and Power BI

---

#### Manager View (Company-Wide Data)
![Manager Dashboard](https://via.placeholder.com/800x600/764ba2/ffffff?text=Manager+Dashboard)

**Access:** All data from their company (all departments)

**Interactive Colored Stat Cards:**
- 🔵 **Company Users** (Blue)
- 🟢 **Company PRs** (Green)
- 🟣 **Company POs** (Purple)
- 🟠 **Company Assets** (Orange)
- 🔵 **Company PO Value** (Teal)
- 🔴 **Company Stock Items** (Red)

**Charts & Graphs:**
- 📊 PR Status by Status (Doughnut chart)
- 📈 Monthly PR Trends (Line chart)
- 📊 Company Assets by Condition (Bar chart)

**Data Tables:**
- Department PR counts within company
- Recent company purchase requests
- Company stock items

**Export:** Company-wide data export to CSV and Power BI

---

#### Regular User / Requestor View (Personal + Department Data)
![User Dashboard](https://via.placeholder.com/800x600/28a745/ffffff?text=User+Dashboard)

**Access:** Own data + their department's data

**Interactive Colored Stat Cards:**
- 🔵 **My Purchase Requests** (Blue)
- 🟠 **Pending Approval** (Orange)
- 🟢 **Approved** (Green)
- 🟣 **My Total Value** (Purple)
- 🔵 **My Inventory** (Teal)

**Charts & Graphs:**
- 📊 My PR Status Distribution (Doughnut chart)
- 📈 My Monthly PR Trends (Line chart)

**Personal Data Tables:**
- My recent purchase requests with status badges
- My inventory items with stock status

### Stock & Inventory Management
- **Stock Tracking**: View all stock items (Admin/CEO) or personal items (User)
- **Low Stock Alerts**: Automatic detection and highlighting of low-stock items
- **Stock Details**: SKU, name, quantity, unit price, location, condition

### Version & System Info
![Footer Info](https://via.placeholder.com/800x100/333333/ffffff?text=Footer+Version+Info)

- **Login Page Footer**: Displays Python version, database name, and app version
- **Dashboard Footer**: Shows Python version, database (`moao_db`), and app version from `app_versions` table
- **App Version**: Dynamically fetched from `app_versions` table (falls back to '1.0.0')

### Interactive UI Features
- **Hover Effects**: Cards lift up with shadow on hover
- **Click Interaction**: Click cards to see details
- **Load Animation**: Staggered fade-in animation on page load
- **Color Coding**: Each stat card type has unique color scheme
- **Responsive Design**: Grid layout adapts to screen size

### Database Models
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

3. **For new deployment:** See [deploy_guide.md](deploy_guide.md) for complete deployment instructions including:
   - Database schema migration using `finance/migrations/0001_initial.py`
   - Data restoration using PostgreSQL dump
   - Step-by-step deployment to another server

4. Run migrations (creates Django core tables):
```bash
python3 manage.py migrate
```

5. Start the server:
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
   - **Admin/CEO**: See ALL data across all companies and departments
   - **Manager**: See data from their company only (all departments)
   - **User/Requestor**: See own data + their department's data
4. Export data to CSV or Power BI (role-based filtering applied)
5. View Python version, database info, and app version in page footers

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
- Roles from `roles` table (e.g., 'admin', 'ceo', 'manager', 'User', 'requestor')
- Stored in session upon login
- Dashboard content adapts based on role:

| Role | Data Access Level |
|------|-------------------|
| Admin/CEO | Full access - all companies, all departments |
| Manager | Company-wide - all departments in their company |
| User/Requestor | Personal + department data only |

## Data Filtering Logic

- **Admin/CEO**: `PurchaseRequests.objects.all()` - no filtering
- **Manager**: `PurchaseRequests.objects.filter(department__company=user_company)`
- **User**: `Q(user_id=user_id) | Q(department=user_department)`

## Notes

- Models are set to `managed = False` - Django won't modify existing tables
- Password verification supports Laravel's `$2y$` bcrypt format
- The app reads from an existing Laravel database without migration conflicts
- App version is dynamically fetched from `app_versions` table (falls back to '1.0.0')
- Timezone warnings for naive datetimes can be ignored or fixed by updating model fields

## License

MIT

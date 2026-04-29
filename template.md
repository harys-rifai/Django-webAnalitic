# Django Dashboard Template

This is the dashboard template structure for the Data Analytic Django application.

## File Location
`finance/templates/finance/dashboard.html`

## Template Structure

### 1. Header Section
- Logo/Title: "Data Analytic" with 📊 icon
- User info: Welcome message with date/time (`{% now "l, F j, Y g:i A" %}`)
- Role badge showing current user role
- Logout button

### 2. Stat Cards Grid (`.stats-grid`)
Compact modern cards with gradient background:
- **Active Users** (Blue border) - `{{ total_users }}`
- **Purchase Requests** (Green border) - `{{ total_purchase_requests }}`
- **Purchase Orders** (Purple border) - `{{ total_purchase_orders }}`
- **Total Assets** (Orange border) - `{{ total_assets }}`
- **PO Value Total** (Teal border) - `Rp {{ total_po_value|floatformat:0 }}`
- **Receipts This Month** (Red border) - `{{ monthly_receipts }}`
- **Stock Items** (Blue border) - `{{ total_stock_items }}`
- **Low Stock Items** (Red border) - `{{ low_stock_items }}`
- **Total Tax** (Purple border) - `Rp {{ total_tax|floatformat:0 }}`
- **Total Distributor** (Green border) - `{{ total_distributor }}`

**CSS Classes:**
- `.stat-card` - Base class with gradient background, 12px padding, 20px font-size
- Color modifiers: `.blue`, `.green`, `.purple`, `.orange`, `.teal`, `.red`

### 3. Charts Section

#### CEO/Admin Charts (`.charts-compact` - 2 column grid)
- **My PR Status** (`ceoPRStatusChart`) - Doughnut chart
- **My Monthly Trends** (`ceoMonthlyPRChart`) - Line chart
- **PR vs Approved vs Rejected** (`monthlyPRChart`) - Line chart
- **Revenue vs Expense (CEO)** (`revenueExpenseChart`) - Line chart

#### Main Charts (`.charts-grid`)
- **Asset Conditions** (`assetConditionChart`) - Bar chart
- **Monthly PO Value** (`monthlyPOChart`) - Bar chart

#### User Charts
- **My PR Status** (`myPRStatusChart`) - Doughnut chart
- **My Monthly Trends** (`myMonthlyPRChart`) - Line chart

### 4. Data Tables (Tabbed Interface)
- Departments PR / Company Stocks / Recent Stocks / Recent PRs
- Pagination included (`{% include "finance/pagination.html" %}`)

### 5. Footer
- Python version, database name, app version

## Context Variables Required

### CEO/Admin View
```python
{
    'user_name': str,
    'user_role': str,
    'total_users': int,
    'total_purchase_requests': int,
    'total_purchase_orders': int,
    'total_assets': int,
    'total_po_value': float,
    'monthly_receipts': int,
    'total_stock_items': int,
    'low_stock_items': int,
    'total_tax': float,
    'total_distributor': int,
    'pr_by_status': list,  # [{'status': str, 'count': int}]
    'monthly_pr_labels': list,  # ['Jan', 'Feb', ...]
    'monthly_pr_data': list,  # [10, 20, ...]
    'monthly_pr_approved_data': list,
    'monthly_pr_rejected_data': list,
    'monthly_po_labels': list,
    'monthly_po_data': list,
    'assets_by_condition': list,  # [{'condition': str, 'count': int, 'total_value': float}]
    'dept_pr_count': list,  # [{'name': str, 'pr_count': int}]
    'recent_prs_page': Page,
    'recent_stocks_page': Page,
    'company_stocks_page': Page,
    'python_version': str,
    'db_name': str,
    'app_version': str,
}
```

### User View
```python
{
    'user_name': str,
    'user_role': str,
    'my_pr_count': int,
    'my_pending_count': int,
    'my_approved_count': int,
    'my_total_value': float,
    'my_inventory_count': int,
    'my_pr_by_status': list,
    'my_monthly_pr_labels': list,
    'my_monthly_pr_data': list,
    'my_recent_prs_page': Page,
    'my_recent_stocks_page': Page,
    'python_version': str,
    'db_name': str,
    'app_version': str,
}
```

## Key Charts Configuration

### Chart.js Usage
All charts use Chart.js loaded from CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Canvas ID to JS Mapping
All canvas IDs in HTML must match `document.getElementById()` calls in JavaScript:
- `ceoPRStatusChart` ↔ `getElementById('ceoPRStatusChart')`
- `ceoMonthlyPRChart` ↔ `getElementById('ceoMonthlyPRChart')`
- `monthlyPRChart` ↔ `getElementById('monthlyPRChart')`
- `revenueExpenseChart` ↔ `getElementById('revenueExpenseChart')`
- `assetConditionChart` ↔ `getElementById('assetConditionChart')`
- `monthlyPOChart` ↔ `getElementById('monthlyPOChart')`
- `myPRStatusChart` ↔ `getElementById('myPRStatusChart')`
- `myMonthlyPRChart` ↔ `getElementById('myMonthlyPRChart')`

## CSS Grid Layouts

### Stats Grid
```css
.stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
}
```

### Charts Compact (2 columns)
```css
.charts-compact {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}
```

### Charts Grid (full width)
```css
.charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 20px;
}
```

## Interactive Features

### Tab Functionality
- Uses `.tab-btn` and `.tab-content` classes
- Switches between data tables
- Active tab has `.active` class

### Expand Chart
- Charts in `charts-compact` are clickable
- `onclick="expandChart('chartId')"` expands chart to full view

### Animations
- Stat cards have staggered slide-up animation
- Hover effects on cards (lift + shadow)
- Smooth transitions (0.3s cubic-bezier)

## Notes for Template Modification

1. **Canvas IDs**: Always ensure HTML canvas IDs match JS `getElementById` calls
2. **Role Checks**: Use `{% if user_role == 'admin' or user_role == 'ceo' %}` for CEO view
3. **Conditional Rendering**: Charts only render if data exists (`{% if pr_by_status %}`)
4. **Pagination**: Use `{% include "finance/pagination.html" with page_obj=... %}`
5. **Date/Time**: Welcome section includes `{% now "l, F j, Y g:i A" %}`

import bcrypt
import sys
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .models import (Users, PurchaseRequests, PurchaseOrders, Assets,
                     MaterialReceipts, Departments, Stocks, Roles,
                     RoleUser, AppVersions)

def get_user_role(user_id):
    try:
        role_user = RoleUser.objects.filter(user_id=user_id).select_related('role').first()
        return role_user.role.name if role_user else 'User'
    except:
        return 'User'

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Users.objects.get(email=email)
            if user.password.startswith('$2y$'):
                password_hash = user.password.encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                    if user.active:
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.name
                        request.session['user_email'] = user.email
                        request.session['user_role'] = get_user_role(user.id)
                        messages.success(request, f'Welcome back, {user.name}!')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account is inactive.')
                else:
                    messages.error(request, 'Invalid email or password.')
            else:
                if user.password == password:
                    if user.active:
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.name
                        request.session['user_email'] = user.email
                        request.session['user_role'] = get_user_role(user.id)
                        messages.success(request, f'Welcome back, {user.name}!')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account is inactive.')
                else:
                    messages.error(request, 'Invalid email or password.')
        except Users.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

    # Get Python version and DB info for login page
    python_version = sys.version.split()[0]
    db_name = 'moao_db'
    app_version = AppVersions.objects.order_by('-created_at').first()
    app_version_str = app_version.version if app_version else '1.0.0'

    return render(request, 'finance/login.html', {
        'python_version': python_version,
        'db_name': db_name,
        'app_version': app_version_str,
    })


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_name = request.session.get('user_name', 'User')
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role', 'User')

    from django.db.models import Count, Sum
    from datetime import datetime

    # Get app version
    app_version = AppVersions.objects.order_by('-created_at').first()
    app_version_str = app_version.version if app_version else '1.0.0'

    # Base context
    context = {
        'user_name': user_name,
        'user_role': user_role,
        'python_version': sys.version.split()[0],
        'db_name': 'moao_db',
        'app_version': app_version_str,
    }

    # Role-based analytics
    if user_role == 'admin' or user_role == 'ceo':
        # Admin and CEO see everything
        context['total_users'] = Users.objects.filter(active=True).count()
        context['total_purchase_requests'] = PurchaseRequests.objects.count()
        context['total_purchase_orders'] = PurchaseOrders.objects.count()
        context['total_assets'] = Assets.objects.count()
        context['total_po_value'] = PurchaseOrders.objects.aggregate(total=Sum('total_price'))['total'] or 0
        context['pr_by_status'] = list(PurchaseRequests.objects.values('status').annotate(count=Count('id')))
        context['recent_prs'] = PurchaseRequests.objects.select_related('user', 'department').order_by('-created_at')[:10]
        context['dept_pr_count'] = Departments.objects.annotate(pr_count=Count('purchaserequests')).order_by('-pr_count')[:5]
        today = datetime.now()
        first_day_month = today.replace(day=1)
        context['monthly_receipts'] = MaterialReceipts.objects.filter(received_at__gte=first_day_month).count()
        context['assets_by_condition'] = list(Assets.objects.values('condition').annotate(count=Count('id'), total_value=Sum('purchase_price')))
        # Stock data for admin
        context['total_stock_items'] = Stocks.objects.filter(active=True).count()
        context['low_stock_items'] = Stocks.objects.filter(active=True, low_stock=True).count()
        context['recent_stocks'] = Stocks.objects.select_related('asset', 'user').order_by('-created_at')[:10]

        # Monthly PR trends (last 6 months)
        from django.db.models.functions import TruncMonth
        monthly_pr = PurchaseRequests.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:6]
        context['monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr]
        context['monthly_pr_data'] = [item['count'] for item in monthly_pr]

        # Monthly PO value trends (last 6 months)
        monthly_po = PurchaseOrders.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_price')).order_by('month')[:6]
        context['monthly_po_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_po]
        context['monthly_po_data'] = [float(item['total']) if item['total'] else 0 for item in monthly_po]
    elif user_role == 'User' or 'requestor' in user_role.lower():
        # Regular users see only their data
        user_prs = PurchaseRequests.objects.filter(user_id=user_id)
        context['my_pr_count'] = user_prs.count()
        context['my_pr_pending'] = user_prs.filter(status='pending').count()
        context['my_pr_approved'] = user_prs.filter(status='approved').count()
        context['my_total_value'] = user_prs.aggregate(total=Sum('estimated_price'))['total'] or 0
        context['recent_prs'] = user_prs.select_related('department').order_by('-created_at')[:10]
        # User's stocks/inventory
        context['my_stocks'] = Stocks.objects.filter(user_id=user_id, active=True).order_by('-created_at')[:10]
        context['my_stock_count'] = Stocks.objects.filter(user_id=user_id, active=True).count()
    else:
        # Default user view
        user_prs = PurchaseRequests.objects.filter(user_id=user_id)
        context['my_pr_count'] = user_prs.count()
        context['recent_prs'] = user_prs.order_by('-created_at')[:5]

    return render(request, 'finance/dashboard.html', context)

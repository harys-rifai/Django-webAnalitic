import bcrypt
import sys
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
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
    from datetime import datetime, timedelta
    import calendar

    # Get filter parameters
    filter_year = request.GET.get('year', str(datetime.now().year))
    filter_month = request.GET.get('month', str(datetime.now().month))
    filter_day = request.GET.get('day', '')

    # Parse filters
    try:
        filter_year_int = int(filter_year)
        filter_month_int = int(filter_month)
    except:
        filter_year_int = datetime.now().year
        filter_month_int = datetime.now().month

    # Build date filter
    date_filter = {}
    if filter_year_int:
        date_filter['year'] = filter_year_int
    if filter_month_int:
        date_filter['month'] = filter_month_int
    if filter_day:
        try:
            date_filter['day'] = int(filter_day)
        except:
            pass

    # Get available years for filter
    from django.db.models.functions import ExtractYear
    available_years = PurchaseRequests.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
    available_years = [y for y in available_years if y]

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
        'filter_year': filter_year,
        'filter_month': filter_month,
        'filter_day': filter_day,
        'available_years': available_years,
        'available_months': [(str(i), calendar.month_name[i]) for i in range(1, 13)],
    }

    # Role-based analytics
    if user_role == 'admin' or user_role == 'ceo':
        # Apply filters to querysets
        pr_query = PurchaseRequests.objects.all()
        po_query = PurchaseOrders.objects.all()
        receipts_query = MaterialReceipts.objects.all()

        if filter_year:
            pr_query = pr_query.filter(created_at__year=filter_year_int)
            po_query = po_query.filter(created_at__year=filter_year_int)
            receipts_query = receipts_query.filter(received_at__year=filter_year_int)
        if filter_month:
            pr_query = pr_query.filter(created_at__month=filter_month_int)
            po_query = po_query.filter(created_at__month=filter_month_int)
            receipts_query = receipts_query.filter(received_at__month=filter_month_int)
        if filter_day:
            try:
                pr_query = pr_query.filter(created_at__day=int(filter_day))
                po_query = po_query.filter(created_at__day=int(filter_day))
                receipts_query = receipts_query.filter(received_at__day=int(filter_day))
            except:
                pass

        context['total_users'] = Users.objects.filter(active=True).count()
        context['total_purchase_requests'] = pr_query.count()
        context['total_purchase_orders'] = po_query.count()
        context['total_assets'] = Assets.objects.count()
        context['total_po_value'] = po_query.aggregate(total=Sum('total_price'))['total'] or 0
        context['pr_by_status'] = list(pr_query.values('status').annotate(count=Count('id')))
        context['recent_prs'] = pr_query.select_related('user', 'department').order_by('-created_at')[:10]
        context['dept_pr_count'] = Departments.objects.annotate(pr_count=Count('purchaserequests')).order_by('-pr_count')[:5]

        # Monthly filter for receipts
        first_day_month = datetime(filter_year_int, filter_month_int, 1)
        next_month = first_day_month.replace(day=28) + timedelta(days=4)
        last_day_month = next_month - timedelta(days=next_month.day)
        context['monthly_receipts'] = receipts_query.filter(received_at__range=(first_day_month, last_day_month)).count()

        context['assets_by_condition'] = list(Assets.objects.values('condition').annotate(count=Count('id'), total_value=Sum('purchase_price')))
        context['total_stock_items'] = Stocks.objects.filter(active=True).count()
        context['low_stock_items'] = Stocks.objects.filter(active=True, low_stock=True).count()
        context['recent_stocks'] = Stocks.objects.select_related('asset', 'user').order_by('-created_at')[:10]

        # Monthly PR trends (last 6 months) with filter
        from django.db.models.functions import TruncMonth
        monthly_pr = PurchaseRequests.objects.filter(created_at__year=filter_year_int).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:6]
        context['monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr]
        context['monthly_pr_data'] = [item['count'] for item in monthly_pr]

        # Monthly PR approved
        monthly_pr_approved = PurchaseRequests.objects.filter(created_at__year=filter_year_int, status='approved').annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:6]
        context['monthly_pr_approved_data'] = [item['count'] for item in monthly_pr_approved]

        # Monthly PR rejected
        monthly_pr_rejected = PurchaseRequests.objects.filter(created_at__year=filter_year_int, status='rejected').annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:6]
        context['monthly_pr_rejected_data'] = [item['count'] for item in monthly_pr_rejected]

        # Monthly PO released (value)
        monthly_po = PurchaseOrders.objects.filter(created_at__year=filter_year_int).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_price')).order_by('month')[:6]
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

        # User-specific charts data
        my_pr_by_status = user_prs.values('status').annotate(count=Count('id'))
        context['my_pr_by_status'] = list(my_pr_by_status)

        from django.db.models.functions import TruncMonth
        my_monthly_pr = user_prs.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:6]
        context['my_monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in my_monthly_pr]
        context['my_monthly_pr_data'] = [item['count'] for item in my_monthly_pr]
    else:
        # Default user view
        user_prs = PurchaseRequests.objects.filter(user_id=user_id)
        context['my_pr_count'] = user_prs.count()
        context['recent_prs'] = user_prs.order_by('-created_at')[:5]

    return render(request, 'finance/dashboard.html', context)


def export_csv(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_role = request.session.get('user_role', 'User')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dashboard_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Item', 'Quantity', 'Price', 'Status', 'Date'])

    if user_role == 'admin' or user_role == 'ceo':
        prs = PurchaseRequests.objects.select_related('user', 'department').order_by('-created_at')[:100]
        for pr in prs:
            writer.writerow(['PR', pr.item_name, pr.qty, pr.estimated_price, pr.status, pr.created_at])
    else:
        user_id = request.session.get('user_id')
        prs = PurchaseRequests.objects.filter(user_id=user_id).order_by('-created_at')[:50]
        for pr in prs:
            writer.writerow(['PR', pr.item_name, pr.qty, pr.estimated_price, pr.status, pr.created_at])

    return response


def share_teams(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_name = request.session.get('user_name', 'User')
    dashboard_url = request.build_absolute_uri('/dashboard/')

    # Return a page with Teams share link
    teams_url = f"https://teams.microsoft.com/l/chat/0/0?users=&message=Check%20out%20this%20dashboard:%20{dashboard_url}"

    return render(request, 'finance/share.html', {
        'share_url': teams_url,
        'platform': 'Microsoft Teams',
        'user_name': user_name,
    })


def share_chat(request):
    if not request.session.get('user_id'):
        return redirect('login')

    dashboard_url = request.build_absolute_uri('/dashboard/')
    chat_url = f"https://wa.me/?text=Check%20out%20this%20dashboard:%20{dashboard_url}"

    return render(request, 'finance/share.html', {
        'share_url': chat_url,
        'platform': 'WhatsApp',
        'user_name': request.session.get('user_name', 'User'),
    })


def power_bi_export(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_role = request.session.get('user_role', 'User')

    # Generate Power BI compatible data
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="power_bi_data.json"'

    import json
    from django.http import JsonResponse
    from django.db.models import Count, Sum

    data = {}

    if user_role == 'admin' or user_role == 'ceo':
        pr_by_status = list(PurchaseRequests.objects.values('status').annotate(count=Count('id')))
        data['pr_by_status'] = pr_by_status
        data['total_pr'] = PurchaseRequests.objects.count()
        data['total_po'] = PurchaseOrders.objects.count()
        data['total_assets'] = Assets.objects.count()
    else:
        user_id = request.session.get('user_id')
        my_prs = PurchaseRequests.objects.filter(user_id=user_id)
        data['my_pr_count'] = my_prs.count()
        data['my_pr_by_status'] = list(my_prs.values('status').annotate(count=Count('id')))

    return JsonResponse(data)

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
        return role_user.role.name.lower() if role_user else 'user'
    except:
        return 'user'

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


def get_user_company_departments(user):
    """Get company and departments based on user role"""
    try:
        current_user = Users.objects.get(id=user.id)
        return current_user.company, current_user.department, current_user
    except:
        return None, None, None

def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_name = request.session.get('user_name', 'User')
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role', 'user')

    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    import calendar

    app_version = AppVersions.objects.order_by('-created_at').first()
    app_version_str = app_version.version if app_version else '1.0.0'

    filter_month = request.GET.get('month', str(datetime.now().month))
    filter_day = request.GET.get('day', '')

    try:
        filter_month_int = int(filter_month)
    except:
        filter_month_int = datetime.now().month

    available_months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]

    from django.db.models.functions import ExtractYear
    available_years = PurchaseRequests.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
    available_years = [y for y in available_years if y]

    from django.core.paginator import Paginator
    page_number = request.GET.get('page', 1)
    per_page = 10

    context = {
        'user_name': user_name,
        'user_role': user_role,
        'python_version': sys.version.split()[0],
        'db_name': 'moao_db',
        'app_version': app_version_str,
        'filter_month': filter_month,
        'filter_day': filter_day,
        'available_months': available_months,
        'available_years': available_years,
    }

    # Get user's company and department for filtering
    try:
        current_user = Users.objects.get(id=user_id)
        user_company = current_user.company
        user_department = current_user.department
    except Users.DoesNotExist:
        current_user = None
        user_company = None
        user_department = None

    # CEO/Admin: See all data
    if user_role in ['admin', 'ceo']:
        pr_query = PurchaseRequests.objects.all()
        po_query = PurchaseOrders.objects.all()
        receipts_query = MaterialReceipts.objects.all()
        stocks_query = Stocks.objects.filter(active=True)
        assets_query = Assets.objects.all()

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
        context['total_assets'] = assets_query.count()
        context['total_po_value'] = po_query.aggregate(total=Sum('total_price'))['total'] or 0
        context['monthly_receipts'] = receipts_query.count()
        context['pr_by_status'] = list(pr_query.values('status').annotate(count=Count('id')))

        recent_prs_paginator = Paginator(pr_query.select_related('user', 'department').order_by('-created_at'), per_page)
        recent_prs_page = recent_prs_paginator.get_page(page_number)
        context['recent_prs'] = recent_prs_page
        context['recent_prs_paginator'] = recent_prs_paginator
        context['recent_prs_page'] = recent_prs_page

        context['dept_pr_count'] = Departments.objects.annotate(pr_count=Count('purchaserequests')).order_by('-pr_count')[:5]

        context['assets_by_condition'] = list(assets_query.values('condition').annotate(count=Count('id'), total_value=Sum('purchase_price')))
        context['total_stock_items'] = stocks_query.count()
        context['low_stock_items'] = stocks_query.filter(low_stock=True).count()

        stocks_paginator = Paginator(stocks_query.select_related('asset', 'user').order_by('-created_at'), per_page)
        stocks_page = stocks_paginator.get_page(page_number)
        context['recent_stocks'] = stocks_page
        context['stocks_paginator'] = stocks_paginator
        context['stocks_page'] = stocks_page

        from django.db.models.functions import TruncMonth
        monthly_pr = list(PurchaseRequests.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        monthly_pr = monthly_pr[::-1]
        context['monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr]
        context['monthly_pr_data'] = [item['count'] for item in monthly_pr]

        monthly_pr_approved = list(PurchaseRequests.objects.filter(status__in=['approved_line', 'approved_ceo']).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        monthly_pr_approved = monthly_pr_approved[::-1]
        context['monthly_pr_approved_data'] = [item['count'] for item in monthly_pr_approved]

        monthly_pr_rejected = list(PurchaseRequests.objects.filter(status='rejected').annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        monthly_pr_rejected = monthly_pr_rejected[::-1]
        context['monthly_pr_rejected_data'] = [item['count'] for item in monthly_pr_rejected]

        monthly_po = list(PurchaseOrders.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_price')).order_by('-month')[:12])
        monthly_po = monthly_po[::-1]
        context['monthly_po_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_po]
        context['monthly_po_data'] = [float(item['total']) if item['total'] else 0 for item in monthly_po]

        monthly_pr_value = list(PurchaseRequests.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('estimated_price')).order_by('-month')[:12])
        monthly_pr_value = monthly_pr_value[::-1]
        context['monthly_pr_value_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr_value]
        context['monthly_pr_value_data'] = [float(item['total']) if item['total'] else 0 for item in monthly_pr_value]

    # Manager: See data from their company and all departments
    elif 'manager' in user_role.lower():
        if user_company:
            # Get all departments in the same company
            company_departments = Departments.objects.filter(company=user_company)
            pr_query = PurchaseRequests.objects.filter(department__company=user_company)
            po_query = PurchaseOrders.objects.filter(request__department__company=user_company)
            receipts_query = MaterialReceipts.objects.filter(po__request__department__company=user_company)
            stocks_query = Stocks.objects.filter(active=True, user__company=user_company)
            assets_query = Assets.objects.filter(purchase_request__department__company=user_company)
        else:
            pr_query = PurchaseRequests.objects.none()
            po_query = PurchaseOrders.objects.none()
            receipts_query = MaterialReceipts.objects.none()
            stocks_query = Stocks.objects.none()
            assets_query = Assets.objects.none()

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

        context['total_users'] = Users.objects.filter(company=user_company, active=True).count() if user_company else 0
        context['total_purchase_requests'] = pr_query.count()
        context['total_purchase_orders'] = po_query.count()
        context['total_assets'] = assets_query.count()
        context['total_po_value'] = po_query.aggregate(total=Sum('total_price'))['total'] or 0
        context['monthly_receipts'] = receipts_query.count()
        context['pr_by_status'] = list(pr_query.values('status').annotate(count=Count('id')))

        recent_prs_paginator = Paginator(pr_query.select_related('user', 'department').order_by('-created_at'), per_page)
        recent_prs_page = recent_prs_paginator.get_page(page_number)
        context['recent_prs'] = recent_prs_page
        context['recent_prs_paginator'] = recent_prs_paginator
        context['recent_prs_page'] = recent_prs_page

        context['dept_pr_count'] = Departments.objects.filter(company=user_company).annotate(pr_count=Count('purchaserequests')).order_by('-pr_count')[:5] if user_company else []

        context['assets_by_condition'] = list(assets_query.values('condition').annotate(count=Count('id'), total_value=Sum('purchase_price')))
        context['total_stock_items'] = stocks_query.count()
        context['low_stock_items'] = stocks_query.filter(low_stock=True).count()

        stocks_paginator = Paginator(stocks_query.select_related('asset', 'user').order_by('-created_at'), per_page)
        stocks_page = stocks_paginator.get_page(page_number)
        context['recent_stocks'] = stocks_page
        context['stocks_paginator'] = stocks_paginator
        context['stocks_page'] = stocks_page

        from django.db.models.functions import TruncMonth
        monthly_pr = list(pr_query.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        monthly_pr = monthly_pr[::-1]
        context['monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr]
        context['monthly_pr_data'] = [item['count'] for item in monthly_pr]

        monthly_pr_value = list(pr_query.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('estimated_price')).order_by('-month')[:12])
        monthly_pr_value = monthly_pr_value[::-1]
        context['monthly_pr_value_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in monthly_pr_value]
        context['monthly_pr_value_data'] = [float(item['total']) if item['total'] else 0 for item in monthly_pr_value]

        # Manager graphs
        context['monthly_po_labels'] = []
        context['monthly_po_data'] = []
        context['monthly_pr_approved_data'] = []
        context['monthly_pr_rejected_data'] = []

    # Regular User/Requestor: See own data and department data
    else:
        from django.db.models import Q
        if user_department:
            filtered_prs = PurchaseRequests.objects.filter(
                Q(user_id=user_id) | Q(department=user_department)
            )
        elif user_company:
            filtered_prs = PurchaseRequests.objects.filter(
                Q(user_id=user_id) | Q(department__company=user_company)
            )
        else:
            filtered_prs = PurchaseRequests.objects.filter(user_id=user_id)

        if filter_month:
            filtered_prs = filtered_prs.filter(created_at__month=filter_month_int)
        if filter_day:
            try:
                filtered_prs = filtered_prs.filter(created_at__day=int(filter_day))
            except:
                pass

        context['my_pr_count'] = filtered_prs.count()
        context['my_pr_pending'] = filtered_prs.filter(status='pending').count()
        context['my_pr_approved'] = filtered_prs.filter(status__in=['approved', 'approved_line', 'approved_ceo']).count()
        context['my_pr_rejected'] = filtered_prs.filter(status='rejected').count()
        context['my_total_value'] = filtered_prs.aggregate(total=Sum('estimated_price'))['total'] or 0

        my_prs_paginator = Paginator(filtered_prs.select_related('user', 'department').order_by('-created_at'), per_page)
        my_prs_page = my_prs_paginator.get_page(page_number)
        context['recent_prs'] = my_prs_page
        context['recent_prs_paginator'] = my_prs_paginator
        context['recent_prs_page'] = my_prs_page

        my_stocks_paginator = Paginator(Stocks.objects.filter(user_id=user_id, active=True).order_by('-created_at'), per_page)
        my_stocks_page = my_stocks_paginator.get_page(page_number)
        context['my_stocks'] = my_stocks_page
        context['my_stocks_paginator'] = my_stocks_paginator
        context['my_stocks_page'] = my_stocks_page
        context['my_stock_count'] = Stocks.objects.filter(user_id=user_id, active=True).count()

        my_pr_by_status = filtered_prs.values('status').annotate(count=Count('id'))
        context['my_pr_by_status'] = list(my_pr_by_status)

        from django.db.models.functions import TruncMonth
        my_monthly_pr = list(filtered_prs.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')[:12])
        context['my_monthly_pr_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in my_monthly_pr]
        context['my_monthly_pr_data'] = [item['count'] for item in my_monthly_pr]

        my_monthly_pr_value = list(filtered_prs.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('estimated_price')).order_by('month')[:12])
        context['my_monthly_pr_value_labels'] = [item['month'].strftime('%b %Y') if item['month'] else '' for item in my_monthly_pr_value]
        context['my_monthly_pr_value_data'] = [float(item['total']) if item['total'] else 0 for item in my_monthly_pr_value]

    return render(request, 'finance/dashboard.html', context)


def export_csv(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role', 'User')

    try:
        current_user = Users.objects.get(id=user_id)
        user_company = current_user.company
        user_department = current_user.department
    except Users.DoesNotExist:
        return redirect('login')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dashboard_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Item', 'Quantity', 'Price', 'Status', 'Date', 'User', 'Department'])

    from django.db.models import Q

    if user_role in ['admin', 'ceo']:
        # CEO/Admin: Export all data
        prs = PurchaseRequests.objects.select_related('user', 'department').order_by('-created_at')
        for pr in prs:
            writer.writerow(['PR', pr.item_name, pr.qty, pr.estimated_price, pr.status, pr.created_at, pr.user.name if pr.user else '', pr.department.name if pr.department else ''])

    elif 'manager' in user_role.lower():
        # Manager: Export data from their company
        if user_company:
            prs = PurchaseRequests.objects.filter(department__company=user_company).select_related('user', 'department').order_by('-created_at')
            for pr in prs:
                writer.writerow(['PR', pr.item_name, pr.qty, pr.estimated_price, pr.status, pr.created_at, pr.user.name if pr.user else '', pr.department.name if pr.department else ''])
        else:
            writer.writerow(['No company associated with manager'])

    else:
        # User/Requestor: Export own data and department data
        if user_department:
            prs = PurchaseRequests.objects.filter(
                Q(user_id=user_id) | Q(department=user_department)
            ).select_related('user', 'department').order_by('-created_at')
        else:
            prs = PurchaseRequests.objects.filter(user_id=user_id).select_related('user', 'department').order_by('-created_at')

        for pr in prs:
            writer.writerow(['PR', pr.item_name, pr.qty, pr.estimated_price, pr.status, pr.created_at, pr.user.name if pr.user else '', pr.department.name if pr.department else ''])

    return response


def share_teams(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_name = request.session.get('user_name', 'User')
    dashboard_url = request.build_absolute_uri('/dashboard/')

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

    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role', 'User')

    try:
        current_user = Users.objects.get(id=user_id)
        user_company = current_user.company
        user_department = current_user.department
    except Users.DoesNotExist:
        return redirect('login')

    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="power_bi_data.json"'

    import json
    from django.http import JsonResponse
    from django.db.models import Count, Sum, Q

    data = {}

    if user_role in ['admin', 'ceo']:
        # CEO/Admin: All data
        pr_by_status = list(PurchaseRequests.objects.values('status').annotate(count=Count('id')))
        data['pr_by_status'] = pr_by_status
        data['total_pr'] = PurchaseRequests.objects.count()
        data['total_po'] = PurchaseOrders.objects.count()
        data['total_assets'] = Assets.objects.count()

        # Monthly PR data
        from django.db.models.functions import TruncMonth
        monthly_pr = list(PurchaseRequests.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        data['monthly_pr'] = [{'month': item['month'].strftime('%b %Y') if item['month'] else '', 'count': item['count']} for item in monthly_pr]

    elif 'manager' in user_role.lower():
        # Manager: Company data only
        if user_company:
            pr_query = PurchaseRequests.objects.filter(department__company=user_company)
            pr_by_status = list(pr_query.values('status').annotate(count=Count('id')))
            data['pr_by_status'] = pr_by_status
            data['total_pr'] = pr_query.count()
            data['total_po'] = PurchaseOrders.objects.filter(request__department__company=user_company).count()
            data['total_assets'] = Assets.objects.filter(purchase_request__department__company=user_company).count()

            from django.db.models.functions import TruncMonth
            monthly_pr = list(pr_query.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
            data['monthly_pr'] = [{'month': item['month'].strftime('%b %Y') if item['month'] else '', 'count': item['count']} for item in monthly_pr]
        else:
            data['pr_by_status'] = []
            data['total_pr'] = 0

    else:
        # User/Requestor: Own and department data
        if user_department:
            filtered_prs = PurchaseRequests.objects.filter(
                Q(user_id=user_id) | Q(department=user_department)
            )
        else:
            filtered_prs = PurchaseRequests.objects.filter(user_id=user_id)

        data['my_pr_count'] = filtered_prs.count()
        data['my_pr_by_status'] = list(filtered_prs.values('status').annotate(count=Count('id')))

        from django.db.models.functions import TruncMonth
        monthly_pr = list(filtered_prs.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('-month')[:12])
        data['monthly_pr'] = [{'month': item['month'].strftime('%b %Y') if item['month'] else '', 'count': item['count']} for item in monthly_pr]

    return JsonResponse(data)

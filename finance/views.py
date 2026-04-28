import bcrypt
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users, PurchaseRequests, PurchaseOrders, Assets, MaterialReceipts, Departments


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
                        messages.success(request, f'Welcome back, {user.name}!')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account is inactive.')
                else:
                    messages.error(request, 'Invalid email or password.')
        except Users.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'finance/login.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')

    user_name = request.session.get('user_name', 'User')
    user_id = request.session.get('user_id')

    from django.db.models import Count, Sum
    from datetime import datetime

    # Summary statistics
    total_users = Users.objects.filter(active=True).count()
    total_purchase_requests = PurchaseRequests.objects.count()
    total_purchase_orders = PurchaseOrders.objects.count()
    total_assets = Assets.objects.count()

    # Purchase requests by status
    pr_by_status = PurchaseRequests.objects.values('status').annotate(count=Count('id'))

    # Total purchase value
    total_po_value = PurchaseOrders.objects.aggregate(total=Sum('total_price'))['total'] or 0

    # Recent purchase requests
    recent_prs = PurchaseRequests.objects.select_related('user', 'department').order_by('-created_at')[:10]

    # Top departments by PR count
    dept_pr_count = Departments.objects.annotate(pr_count=Count('purchaserequests')).order_by('-pr_count')[:5]

    # Material receipts this month
    today = datetime.now()
    first_day_month = today.replace(day=1)
    monthly_receipts = MaterialReceipts.objects.filter(received_at__gte=first_day_month).count()

    # Asset value by condition
    assets_by_condition = Assets.objects.values('condition').annotate(
        count=Count('id'),
        total_value=Sum('purchase_price')
    )

    context = {
        'user_name': user_name,
        'total_users': total_users,
        'total_purchase_requests': total_purchase_requests,
        'total_purchase_orders': total_purchase_orders,
        'total_assets': total_assets,
        'total_po_value': total_po_value,
        'pr_by_status': list(pr_by_status),
        'recent_prs': recent_prs,
        'dept_pr_count': dept_pr_count,
        'monthly_receipts': monthly_receipts,
        'assets_by_condition': list(assets_by_condition),
    }

    return render(request, 'finance/dashboard.html', context)

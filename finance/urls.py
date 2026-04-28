from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('share/teams/', views.share_teams, name='share_teams'),
    path('share/chat/', views.share_chat, name='share_chat'),
    path('power-bi/export/', views.power_bi_export, name='power_bi_export'),
]

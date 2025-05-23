from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path('', views.LeaveRequestListView.as_view(), name='leave_request_list'),
    path('request/new/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('request/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_request_detail'),
    path('request/<int:pk>/validate/', views.validate_leave_request, name='leave_request_validate'),
    path('request/<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
] 
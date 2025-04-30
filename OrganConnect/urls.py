"""
URL configuration for OrganConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from OcApp import views
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("chatbot/", include("chatbot.urls")),
    path('',views.index,name='index'),
    path('login-register/',views.login_register,name='login_register'),
    path('logout/',views.log_out,name='log_out'),

    path('admin_dash/',views.admin_dash,name='admin_dash'),
    path('doctor_dash/',views.doctor_dash,name='doctor_dash'),
    path('donor_dash/',views.donor_dash,name='donor_dash'),
    path('recipient_dash/',views.recipient_dash,name='recipient_dash'),
    path('facility_dash/',views.facility_dash,name='facility_dash'),
    
    path('users/',views.manage_users,name='manage_users'),
    path('remove_user/<user_id>/',views.remove_user,name='remove_user'),
    path('donor_console/',views.donor_console,name='donor_console'),
    path('save_donor/',views.save_donor,name='save_donor'),
    path('organ_request/',views.organ_request,name='organ_request'),
    path('save_organ_request/',views.save_organ_request,name='save_organ_request'),
    path("donors/", views.donor_list, name="donor_list"),
    path("upload-organ/", views.upload_organ, name="upload_organ"),
    path('organ-inventory/', views.organ_inventory, name='organ_inventory'),
    path('organ_matching/', views.organ_matching, name='organ_matching'),
    path('create-organ-request/', views.create_organ_request, name='create_organ_request'),
    path('organ_approval/', views.organ_approval, name='organ_approval'),
    path('get_allocations/', views.get_allocations, name='get_allocations'),
    path('approve_organ_allocation/<int:allocation_id>/', views.approve_organ_allocation, name='approve_organ_allocation'),
    path('notification', views.notification, name='notification'),
    path('reply-notification/<int:notification_id>/', views.reply_notification, name='reply_notification'),
    path('mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('facility_schedule/', views.facility_schedule, name='facility_schedule'),
    path('schedule_operation/<int:notification_id>/', views.schedule_operation, name='schedule_operation'),
    path('update_staff/', views.update_staff, name='update_staff'),
    path('update_doctor/', views.update_doctor, name='update_doctor'),
    path('new_hospital/', views.request_new_hospital, name='new_hospital'),
    path('hospitals/', views.hospital_verification, name='hospital_verification'),
    path('hospitals/verify/<int:hospital_id>/', views.verify_hospital, name='verify_hospital'),

    path('add_review/', views.add_review, name='add_review'),
    path('schedule-pdf/<int:organ_match_id>', views.schedule_pdf, name='schedule_pdf'),
]

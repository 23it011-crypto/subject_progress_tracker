from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/add_subject/', views.add_subject, name='add_subject'),
    path('hod/manage/', views.manage_subjects, name='manage_subjects'),
    path('hod/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('hod/add_teacher/', views.add_teacher, name='add_teacher'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/update/<int:subject_id>/', views.update_progress, name='update_progress'),
    path('hod/subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('system-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('system-admin/logs/', views.activity_logs, name='activity_logs'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('hod/send_reminder/<int:subject_id>/', views.send_reminder, name='send_reminder'),
]

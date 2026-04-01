from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Avg
from .models import User, Subject, SubjectProgress, DocumentProof, Notification, ActivityLog, Message
from .services import HODService, NotificationService
from django.utils import timezone
from datetime import date

def is_hod(user):
    return user.is_authenticated and user.is_hod

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_admin_or_hod(user):
    return user.is_authenticated and (user.is_admin or user.is_hod)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        elif request.user.is_hod:
            return redirect('hod_dashboard')
        elif request.user.is_teacher:
            return redirect('teacher_dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if user.is_admin:
                return redirect('admin_dashboard')
            elif user.is_hod:
                return redirect('hod_dashboard')
            elif user.is_teacher:
                return redirect('teacher_dashboard')
            else:
                return redirect('login') # Fallback
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(is_admin)
def admin_dashboard(request):
    subjects = Subject.objects.all()
    teachers = User.objects.filter(is_teacher=True)
    return render(request, 'admin_dashboard.html', {'subjects': subjects, 'teachers': teachers})

@user_passes_test(is_admin_or_hod)
def activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'activity_logs.html', {'logs': logs})

@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifs})

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, receiver=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications')

@user_passes_test(is_hod)
def send_reminder(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        unit = request.POST.get('unit')
        msg = f"Complete {unit} for Subject {subject.subject_name}"
        Notification.objects.create(
            receiver=subject.assigned_teacher,
            sender=request.user,
            message=msg
        )
        messages.success(request, 'Reminder sent successfully')
    return redirect('subject_detail', subject_id=subject.id)

@user_passes_test(is_hod)
def hod_dashboard(request):
    year_filter = request.GET.get('year')
    if year_filter and year_filter.isdigit():
        year_filter = int(year_filter)
    else:
        year_filter = None
    
    data = HODService.get_dashboard_data(year_filter)
    teacher_performance = HODService.get_teacher_performance()
    
    context = {
        **data,
        'teacher_performance': teacher_performance,
        'current_year': year_filter
    }
    return render(request, 'hod_dashboard.html', context)

@user_passes_test(is_hod)
def generate_report(request):
    data = HODService.get_dashboard_data()
    return render(request, 'hod_report.html', data)

@login_required
def subject_messages(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    # Authorization: HOD or the assigned teacher
    if not (request.user.is_hod or request.user == subject.assigned_teacher):
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            receiver = subject.assigned_teacher if request.user.is_hod else User.objects.filter(is_hod=True).first()
            Message.objects.create(
                subject=subject,
                sender=request.user,
                receiver=receiver,
                text=text
            )
            Notification.objects.create(
                receiver=receiver,
                sender=request.user,
                message=f"New message regarding {subject.subject_name}: {text[:50]}..."
            )
            messages.success(request, "Message sent.")
            return redirect('subject_messages', subject_id=subject.id)

    chat_messages = Message.objects.filter(subject=subject).order_by('created_at')
    # Mark messages as read
    Message.objects.filter(subject=subject, receiver=request.user).update(is_read=True)
    
    return render(request, 'subject_messages.html', {
        'subject': subject,
        'chat_messages': chat_messages
    })

@user_passes_test(is_admin_or_hod)
def add_subject(request):
    teachers = User.objects.filter(is_teacher=True)
    if request.method == 'POST':
        name = request.POST.get('subject_name')
        code = request.POST.get('course_code')
        sem = request.POST.get('semester')
        units = int(request.POST.get('total_units'))
        tid = request.POST.get('assigned_teacher')
        
        teacher = get_object_or_404(User, pk=tid)
        
        year = int(request.POST.get('year', 1))
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        
        subject = Subject.objects.create(
            subject_name=name,
            course_code=code,
            semester=sem,
            year=year,
            total_units=units,
            start_date=start_date,
            end_date=end_date,
            assigned_teacher=teacher
        )
        
        ActivityLog.objects.create(user=request.user, action="Create Subject", description=f"Subject {name} created")
        # Create initial progress
        SubjectProgress.objects.create(subject=subject)
        
        messages.success(request, 'Subject added successfully')
        return redirect('manage_subjects')
        
    return render(request, 'add_subject.html', {'teachers': teachers})

@user_passes_test(is_admin_or_hod)
def manage_subjects(request):
    year_filter = request.GET.get('year')
    if year_filter and year_filter.isdigit():
        subjects = Subject.objects.filter(year=int(year_filter)).select_related('assigned_teacher', 'progress')
        current_year = int(year_filter)
    else:
        subjects = Subject.objects.all().select_related('assigned_teacher', 'progress')
        current_year = None
    
    teachers = User.objects.filter(is_teacher=True)
    return render(request, 'manage_subjects.html', {
        'subjects': subjects, 
        'teachers': teachers,
        'current_year': current_year
    })

@user_passes_test(is_admin_or_hod)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    subject.delete()
    messages.success(request, 'Subject removed successfully')
    return redirect('manage_subjects')

@user_passes_test(is_teacher)
def teacher_dashboard(request):
    year_filter = request.GET.get('year')
    if year_filter and year_filter.isdigit():
        subjects = Subject.objects.filter(assigned_teacher=request.user, year=int(year_filter)).select_related('progress')
    else:
        subjects = Subject.objects.filter(assigned_teacher=request.user).select_related('progress')
    return render(request, 'teacher_dashboard.html', {'subjects': subjects, 'current_year': int(year_filter) if year_filter and year_filter.isdigit() else None})

@user_passes_test(is_teacher)
def update_progress(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, assigned_teacher=request.user)
    progress = subject.progress
    
    if request.method == 'POST':
        completed_list = request.POST.getlist('units') # List of values from checkboxes
        remarks = request.POST.get('remarks')
        
        proof_file = request.FILES.get('proof_file')
        
        if not remarks or not remarks.strip():
            messages.error(request, 'Message (Remarks) is required to update progress.')
            return redirect('update_progress', subject_id=subject.id)
            
        progress.update_progress(completed_list)
        progress.remarks = remarks
        progress.save()
        
        if proof_file:
            DocumentProof.objects.create(subject=subject, teacher=request.user, file=proof_file)
        
        ActivityLog.objects.create(user=request.user, action="Update Progress", description=f"Updated progress for {subject.subject_name}")
        
        # Send Notification to HODs
        hods = User.objects.filter(is_hod=True)
        for hod in hods:
            Notification.objects.create(
                receiver=hod,
                sender=request.user,
                message=f"Subject: {subject.subject_name}\nTeacher: {request.user.username}\nProgress Remarks: {remarks}"
            )
            
        # Check auto-deadline smart alerts
        if subject.end_date and date.today() > subject.end_date and progress.progress_percentage < 100:
            for hod in hods:
                Notification.objects.create(
                    receiver=hod,
                    sender=None,
                    message=f"Alert: Subject {subject.subject_name} is behind schedule. Deadline passed."
                )
        
        messages.success(request, 'Progress updated successfully')
        return redirect('teacher_dashboard')
    
    # Generate range for template: 1 to total_units
    total_units_range = range(1, subject.total_units + 1)
    completed_units_list = progress.get_completed_list()
    completed_units_int_list = [int(u) for u in completed_units_list if u]
    
    smart_suggestion = None
    if subject.start_date and subject.end_date:
        today = date.today()
        if today > subject.end_date and progress.progress_percentage < 100:
            smart_suggestion = "You are behind schedule. The deadline has passed!"
        elif today >= subject.start_date:
            total_days = (subject.end_date - subject.start_date).days
            days_passed = (today - subject.start_date).days
            expected_progress = (days_passed / total_days) * 100 if total_days > 0 else 100
            
            if progress.progress_percentage < expected_progress - 10:  # 10% tolerance
                suggested_units = max(1, int((expected_progress / 100) * subject.total_units))
                smart_suggestion = f"You are falling behind schedule. Try completing up to Unit {suggested_units} this week."
            elif progress.progress_percentage >= expected_progress:
                smart_suggestion = "Great job! You are on track with the syllabus schedule."
    
    context = {
        'subject': subject,
        'progress': progress,
        'total_units_range': total_units_range,
        'completed_units_list': completed_units_list,
        'checked_units': completed_units_int_list,
        'smart_suggestion': smart_suggestion
    }
    return render(request, 'update_progress.html', context)

@user_passes_test(is_admin_or_hod)
def add_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Basic validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'add_teacher.html')
            
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_teacher = True
            user.save()
            ActivityLog.objects.create(user=request.user, action="Add Teacher", description=f"Teacher {username} added")
            messages.success(request, f'Teacher "{username}" added successfully')
            if request.user.is_admin:
                return redirect('admin_dashboard')
            return redirect('hod_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating teacher: {e}')
            
    return render(request, 'add_teacher.html')

@user_passes_test(is_hod)
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject.objects.select_related('assigned_teacher', 'progress'), pk=subject_id)
    return render(request, 'subject_detail.html', {'subject': subject})

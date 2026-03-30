from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from .models import User, Subject, SubjectProgress
from django.utils import timezone

def is_hod(user):
    return user.is_authenticated and user.is_hod

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if user.is_hod:
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

@user_passes_test(is_hod)
def hod_dashboard(request):
    subjects = Subject.objects.all().select_related('assigned_teacher', 'progress')
    total_subjects = subjects.count()
    completed_subjects = subjects.filter(progress__progress_percentage=100).count()
    pending_subjects = total_subjects - completed_subjects
    
    context = {
        'subjects': subjects,
        'total_subjects': total_subjects,
        'completed_subjects': completed_subjects,
        'pending_subjects': pending_subjects
    }
    return render(request, 'hod_dashboard.html', context)

@user_passes_test(is_hod)
def add_subject(request):
    teachers = User.objects.filter(is_teacher=True)
    if request.method == 'POST':
        name = request.POST.get('subject_name')
        code = request.POST.get('course_code')
        sem = request.POST.get('semester')
        units = int(request.POST.get('total_units'))
        tid = request.POST.get('assigned_teacher')
        
        teacher = get_object_or_404(User, pk=tid)
        
        subject = Subject.objects.create(
            subject_name=name,
            course_code=code,
            semester=sem,
            total_units=units,
            assigned_teacher=teacher
        )
        # Create initial progress
        SubjectProgress.objects.create(subject=subject)
        
        messages.success(request, 'Subject added successfully')
        return redirect('manage_subjects')
        
    return render(request, 'add_subject.html', {'teachers': teachers})

@user_passes_test(is_hod)
def manage_subjects(request):
    subjects = Subject.objects.all()
    teachers = User.objects.filter(is_teacher=True)
    return render(request, 'manage_subjects.html', {'subjects': subjects, 'teachers': teachers})

@user_passes_test(is_hod)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    subject.delete()
    messages.success(request, 'Subject removed successfully')
    return redirect('manage_subjects')

@user_passes_test(is_teacher)
def teacher_dashboard(request):
    subjects = Subject.objects.filter(assigned_teacher=request.user).select_related('progress')
    return render(request, 'teacher_dashboard.html', {'subjects': subjects})

@user_passes_test(is_teacher)
def update_progress(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, assigned_teacher=request.user)
    progress = subject.progress
    
    if request.method == 'POST':
        completed_list = request.POST.getlist('units') # List of values from checkboxes
        remarks = request.POST.get('remarks')
        
        if not remarks or not remarks.strip():
            messages.error(request, 'Message (Remarks) is required to update progress.')
            return redirect('update_progress', subject_id=subject.id)
            
        progress.update_progress(completed_list)
        progress.remarks = remarks
        progress.save()
        
        messages.success(request, 'Progress updated successfully')
        return redirect('teacher_dashboard')
    
    # Generate range for template: 1 to total_units
    total_units_range = range(1, subject.total_units + 1)
    completed_units_list = progress.get_completed_list()
    completed_units_int_list = [int(u) for u in completed_units_list if u]
    
    context = {
        'subject': subject,
        'progress': progress,
        'total_units_range': total_units_range,
        'completed_units_list': completed_units_list,
        'checked_units': completed_units_int_list
    }
    return render(request, 'update_progress.html', context)

@user_passes_test(is_hod)
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
            messages.success(request, f'Teacher "{username}" added successfully')
            return redirect('hod_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating teacher: {e}')
            
    return render(request, 'add_teacher.html')

@user_passes_test(is_hod)
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject.objects.select_related('assigned_teacher', 'progress'), pk=subject_id)
    return render(request, 'subject_detail.html', {'subject': subject})

from django.db.models import Avg, Count, F, Q
from .models import Subject, User, SubjectProgress, Notification, Message, ActivityLog
from datetime import date

class HODService:
    @staticmethod
    def get_dashboard_data(year_filter=None):
        subjects = Subject.objects.all().select_related('assigned_teacher', 'progress')
        if year_filter:
            subjects = subjects.filter(year=year_filter)
        
        total_subjects = subjects.count()
        completed_subjects = subjects.filter(progress__progress_percentage__gte=100).count()
        avg_progress = subjects.aggregate(Avg('progress__progress_percentage'))['progress__progress_percentage__avg'] or 0
        
        return {
            'subjects': subjects,
            'total_subjects': total_subjects,
            'completed_subjects': completed_subjects,
            'pending_subjects': total_subjects - completed_subjects,
            'avg_progress': round(avg_progress, 2)
        }

    @staticmethod
    def get_teacher_performance():
        teachers = User.objects.filter(is_teacher=True).prefetch_related('subjects__progress')
        performance = []
        for teacher in teachers:
            subs = teacher.subjects.all()
            count = subs.count()
            if count > 0:
                avg_p = sum(s.progress.progress_percentage for s in subs) / count
                delayed = sum(1 for s in subs if s.get_expected_progress() > s.progress.progress_percentage)
            else:
                avg_p = 0
                delayed = 0
            performance.append({
                'teacher': teacher,
                'subject_count': count,
                'avg_progress': round(avg_p, 2),
                'delayed_count': delayed
            })
        return performance

class NotificationService:
    @staticmethod
    def check_and_trigger_alerts():
        subjects = Subject.objects.all().select_related('assigned_teacher', 'progress')
        today = date.today()
        hods = User.objects.filter(is_hod=True)
        
        for sub in subjects:
            expected = sub.get_expected_progress()
            actual = sub.progress.progress_percentage
            
            # Alert if behind schedule by more than 10%
            if expected > actual + 10:
                for hod in hods:
                    Notification.objects.get_or_create(
                        receiver=hod,
                        message=f"Urgent: {sub.subject_name} is behind schedule (Expected: {expected}%, Actual: {actual}%)",
                        is_read=False
                    )
            
            # No update for 7 days
            days_since_update = (timezone.now() - sub.progress.last_updated).days
            if days_since_update > 7:
                for hod in hods:
                    Notification.objects.get_or_create(
                        receiver=hod,
                        message=f"Idle: No progress update for {sub.subject_name} in {days_since_update} days.",
                        is_read=False
                    )

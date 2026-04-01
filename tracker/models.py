from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_hod = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Subject(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]
    subject_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20)
    semester = models.IntegerField()
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    total_units = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    assigned_teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_teacher': True}, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def get_expected_progress(self):
        if not self.start_date or not self.end_date:
            return 0.0
        from datetime import date
        today = date.today()
        if today < self.start_date:
            return 0.0
        if today > self.end_date:
            return 100.0
        total_days = (self.end_date - self.start_date).days
        days_passed = (today - self.start_date).days
        return round((days_passed / total_days) * 100, 2) if total_days > 0 else 100.0

    def __str__(self):
        return f"{self.subject_name} ({self.course_code})"

class SubjectProgress(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE, related_name='progress')
    completed_units = models.CharField(max_length=255, default="", blank=True, help_text="Comma-separated list of completed units")
    progress_percentage = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True, null=True)

    def update_progress(self, units_list):
        # units_list is a list of unit strings/numbers
        unique_units = sorted(list(set(units_list)))
        if not unique_units:
            self.completed_units = ""
            count = 0
        else:
            self.completed_units = ",".join(map(str, unique_units))
            count = len(unique_units)
        
        if self.subject.total_units > 0:
            self.progress_percentage = (count / self.subject.total_units) * 100
        else:
            self.progress_percentage = 0.0
        self.save()

    def get_completed_list(self):
        if not self.completed_units:
            return []
        return self.completed_units.split(',')

    def __str__(self):
        return f"Progress for {self.subject.subject_name}"

class DocumentProof(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='proofs')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.subject.subject_name} by {self.teacher.username}"

class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.receiver.username}"

class Message(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender} to {self.receiver} re: {self.subject}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user.username if self.user else 'System'}"

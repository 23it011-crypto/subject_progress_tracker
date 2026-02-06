from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_hod = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20)
    semester = models.IntegerField()
    total_units = models.IntegerField()
    assigned_teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_teacher': True}, related_name='subjects')

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

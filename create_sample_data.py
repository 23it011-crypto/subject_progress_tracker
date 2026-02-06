import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subject_tracker.settings')
django.setup()

from tracker.models import User, Subject, SubjectProgress

def create_data():
    print("Creating sample data...")
    
    # HOD
    if not User.objects.filter(username='hod').exists():
        User.objects.create_superuser('hod', 'hod@example.com', 'hodpassword', is_hod=True)
        print("Created HOD User: username='hod', password='hodpassword'")
    else:
        print("HOD User already exists.")

    # Teachers
    teachers = ['teacher1', 'teacher2']
    teacher_objs = []
    for t in teachers:
        if not User.objects.filter(username=t).exists():
            u = User.objects.create_user(username=t, password='teacherpassword', is_teacher=True)
            print(f"Created Teacher: username='{t}', password='teacherpassword'")
            teacher_objs.append(u)
        else:
            teacher_objs.append(User.objects.get(username=t))

    # Subjects
    subjects_data = [
        ("Advanced Mathematics", "MATH301", 3, 5, teacher_objs[0]),
        ("Data Structures", "CS201", 3, 5, teacher_objs[0]),
        ("Database Systems", "CS202", 3, 5, teacher_objs[1]),
        ("Operating Systems", "CS203", 3, 5, teacher_objs[1]),
    ]

    for name, code, sem, units, tea in subjects_data:
        if not Subject.objects.filter(course_code=code).exists():
            s = Subject.objects.create(subject_name=name, course_code=code, semester=sem, total_units=units, assigned_teacher=tea)
            # Progress is created by signal? No, I did it in view. Check models.
            # I didn't add a signal. I need to create it manually here.
            if not hasattr(s, 'progress'):
                SubjectProgress.objects.create(subject=s)
            print(f"Created Subject: {name} assigned to {tea.username}")
        else:
            # ensure progress exists
            s = Subject.objects.get(course_code=code)
            if not hasattr(s, 'progress'):
                SubjectProgress.objects.create(subject=s)

    print("Sample data creation complete!")

if __name__ == '__main__':
    create_data()

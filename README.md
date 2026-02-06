# Subject Progress Tracker System

## Setup Instructions

1.  **Database Setup**:
    *   Ensure MySQL is running.
    *   Create a database named `subject_tracker_db`.
    *   Update `subject_tracker/settings.py` with your MySQL credentials (User/Password) if different from defaults.

2.  **Environment**:
    *   A virtual environment `venv` has been created. Use it to run commands.
    *   `.\venv\Scripts\activate`

3.  **Run Migrations**:
    ```bash
    python manage.py makemigrations tracker
    python manage.py migrate
    ```

4.  **Create Sample Data**:
    ```bash
    python create_sample_data.py
    ```

5.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## Credentials from Sample Data
*   **HOD Login**: `hod` / `hodpassword`
*   **Teacher Login**: `teacher1` / `teacherpassword`
```
"# subject_progress_tracker" 

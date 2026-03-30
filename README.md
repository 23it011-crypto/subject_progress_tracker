# Subject Progress Tracker System

## Setup Instructions

1.  **Environment**:
    *   A virtual environment `venv` is provided. Activate it to run commands:
    *   `.\venv\Scripts\activate` (Windows)

2.  **Database Setup**:
    *   The project is configured to use **SQLite** (`db.sqlite3`) for easier development.
    *   No separate database server install is required.

3.  **Run migrations and create sample data**:
    ```powershell
    python manage.py migrate
    python manage.py create_sample_data.py
    ```

4.  **Run Server**:
    ```powershell
    python manage.py runserver
    ```

## Credentials from Sample Data
*   **HOD Login**: `hod` / `hodpassword`
*   **Teacher Login**: `teacher1` / `teacherpassword`
```
"# subject_progress_tracker" 

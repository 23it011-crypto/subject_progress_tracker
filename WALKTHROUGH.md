# Project Walkthrough: Subject Tracker 🏆

This project is a professional, **HOD-focused decision support system** designed to monitor, analyze, and manage academic subject progress within an institution. It has been transformed from a basic tracking tool into a smart, efficient, and visually stunning platform.

---

## 🏗️ Project Architecture & Design
The system is built using the **Django Web Framework (Python)** and follows a modern, role-based access control (RBAC) model with enhanced business logic separation.

### 🍱 Technology Stack
- **Backend**: 
  - **Django core**: Business logic moved to `services.py` for better maintainability.
  - **Models**: Enhanced with timeline logic and professional messaging support.
- **Frontend**: 
  - **Glassmorphism UI**: High-end, semi-transparent interface with background blurs and smooth transitions.
  - **Academic Backdrops**: High-resolution, AI-generated professional background imagery.
  - **Premium Branding**: Custom minimalist academic logo icon (stylized book + progress curve).
  - **Vanilla CSS3**: Custom design tokens for a "Premium" feel without external bloat.
- **Data Logic**: 
  - **Timeline Tracking**: Calculates "Expected Progress" vs "Actual Progress" using subject start/end dates.

---

## 👥 User Roles & Permissions

### 1. System Administrator 👑
- **Actions**: Manage Teachers and Subjects, view system-wide **Activity Logs**.

### 2. Head of Department (HOD) 🎓
- **Overview**: Decision-maker focusing on department-wide academic health.
- **Enhanced Features**:
  - **Streamlined Exploration**: Select an **Academic Year** (1st-4th) to immediately filter subjects.
  - **Subject Hub**: Drill down into any subject to see the **Teacher In-Charge** (including direct contact details).
  - **Unified Report**: A single-view grid of ALL subjects (No per-subject clicking required).
  - **Teacher Performance Overview**: Aggregate metrics showing which teachers are on track and who is delayed.
  - **Academic Consultation**: Formal two-way communication channel with teachers regarding specific subjects.
  - **Visual Risk Indicators**: Automatic "At Risk" (Red) highlighting for subjects below 40% or significantly behind schedule.

### 3. Subject Teacher (Tutor) 👨‍🏫
- **Overview**: Tracks and proves syllabus completion.
- **Enhanced Features**:
  - **Progress Update**: Check-box based unit tracking with mandatory remarks and optional document proofs (PDF/Images).
  - **Consultation Portal**: Direct line of sight to HOD's feedback ("Consult with HOD").
  - **Smart Alerts**: Dashboard warnings when falling >10% behind the expected schedule.

---

## 🛠️ Key Professional Enhancements

### 📊 Decision Support & Reporting
- **Expected vs Actual**: The system mathematically determines where a subject *should* be today and calculates the "Delay" percentage.
- **Unified Summary**: One-click PDF-ready reports showing Total Subjects, Completed Subjects, and Average Progress.

### 📧 Academic Consultation System
- **Formal Messaging**: Replaced casual "Chat" with "Academic Consultation" channels.
- **Threaded History**: View full communication logs between HOD and Teachers per subject.
- **Real-time Notifications**: Alerts triggered for new messages, missed updates (idle for 7+ days), or missed deadlines.

### 🎨 Premium Aesthetics
- **Dynamic Backgrounds**: Floating academic icons and abstract nodes create a "State of the Art" educational atmosphere.
- **Professional Branding**: Replaced placeholder text with a dedicated academic icon logo.
- **Isometric Illustrations**: High-quality 3D dashboard visuals for a polished, professional first impression.

---

## 📂 Project Structure (Updated)
- **`tracker/services.py`**: Encapsulates HOD analytics and Notification triggers.
- **`tracker/models.py`**: Added `Message` model and `get_expected_progress` logic.
- **`templates/hod_report.html`**: The new centralized reporting engine.
- **`templates/subject_messages.html`**: The formal consultation portal.
- **`static/images/`**: Contains professional logo, backgrounds, and decorative assets.

---

## 🚀 The Workflow (HOD Focused)
1. **Filtering**: HOD selects "1st Year" on the dashboard to see only entry-level course progress.
2. **Identification**: HOD identifies a subject marked **🔴 At Risk** (e.g., Expected 60%, Actual 30%).
3. **Drill-down**: HOD clicks the subject, sees the **Teacher In-Charge**, and reviews their latest remarks.
4. **Consultation**: HOD clicks **"Consult with Teacher"**, sends a message: "Why is the progress for MATH101 delayed?".
5. **Response**: Teacher receives a notification, replies with an explanation or proof of upcoming assessments.
6. **Resolution**: The "Delay" indicator turns into **"On Track"**, and the system logs the successful intervention.

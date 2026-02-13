# 🚀 LeadSpot CRM – Advanced Lead Management System (Django)

LeadSpot CRM is a production-ready Django-based Lead Management and Sales Tracking System designed to help sales teams manage prospects, track requirements, automate follow-ups, and improve lead conversion efficiency.

This system goes beyond basic CRUD operations and includes smart automation, validation, email workflows, and UX optimizations.

---

## 🏢 Business Problem Solved

Sales teams often struggle with:
- Duplicate leads
- Missed follow-ups
- Poor tracking of requirement stages
- Manual reminder emails
- Inconsistent data entry
- Lost communication records

LeadSpot CRM solves this by providing structured lead tracking with intelligent validation, automated reminders, and stage-based workflow management.

---

# 🔥 Core Features

## 📌 Lead Management
- Create, edit, and manage leads
- Prospect tracking
- Requirement Yes / No classification
- Lost Orders tracking
- Regret Offers tracking
- Customer database view

---

# ⚡ Advanced Enhancements (Implemented)

## 1️⃣ Smart Form Validation
- Required fields show **red alert warnings** if not filled.
- Backend validation prevents invalid entries.
- Duplicate lead suggestion system warns if the same lead already exists.

---

## 2️⃣ Email Deliverability Verification (Backend)
Implemented using:

email-validator (check_deliverability=True)


This prevents fake domains like:
test@thisdomaindoesnotexist123.com


Ensures only real, deliverable email domains are stored.

---

## 3️⃣ Automated Email Workflows

### 📩 Brochure Email Sender
- If brochure was not sent earlier
- Or customer changed email
- Sales team can resend brochure directly from system

---

### 🔁 Reconnect Reminder Mail (Prospect Stage)
- One-click button
- Automatically sends reminder mail
- Helps collect official requirement email

---

### ⏳ Requirement NO Follow-up Automation
- Button to send automatic reminder template
- Configured for 1–2 month follow-up cycle
- Keeps inactive leads warm

---

## 4️⃣ Smart Follow-up Suggestions

In Requirement NO stage:

Dropdown with common reminders:
- Check updates for the project
- Check for any project updates
- Other follow-up templates

This reduces typing time and ensures standard communication.

---

## 5️⃣ Reduced Click UX Optimization

- Date auto-select when opening detail page
- Reduced unnecessary clicks
- Faster workflow for sales team

---

## 6️⃣ Improved Prospect Tracking

- Last updated date visible in Prospect stage
- Date displayed in list view
- Better tracking visibility

---

## 7️⃣ Requirement YES Stage Enhancements

- Sales person name tracking
- "Other" option for flexible assignment
- Requirement preview before saving
- Attachment upload support
- Structured requirement detail view

---

## 8️⃣ Calendar Upgrade

Replaced browser calendar with:

Flatpickr


Provides:
- Better UI
- Consistent formatting
- Improved date selection UX

---

## 9️⃣ Intelligent Duplicate Detection

While typing a lead:
- System suggests existing leads from database
- Prevents duplicate entries
- Maintains clean CRM data

---

# 🛠 Technical Stack

- Python
- Django
- SQLite (Development)
- HTML5
- CSS3
- JavaScript
- Flatpickr
- Email Validator

---

# 📂 Project Structure

LeadSpot/
leads/
templates/
static/
manage.py
requirements.txt


Includes:
- Custom Django Management Command
- Custom Template Filters
- Signal-based automation
- Modular JavaScript per page
- Organized template architecture

---

# ⚙️ Installation Guide

### 1️⃣ Clone Repository

git clone https://github.com/AshOP31244/LeadSpot-CRM-Django.git
cd LeadSpot-CRM-Django


### 2️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate


### 3️⃣ Install Dependencies

pip install -r requirements.txt


### 4️⃣ Apply Migrations

python manage.py migrate


### 5️⃣ Create Superuser

python manage.py createsuperuser


### 6️⃣ Run Server

python manage.py runserver


---

# 📊 Why This Project is Strong for Interviews

This project demonstrates:

- Real-world business logic
- Backend validation
- Email automation
- UX optimization
- Data integrity handling
- Duplicate prevention
- Stage-based workflow architecture
- Clean modular Django structure

This is not a basic CRUD app — this is a practical CRM solution.

---

# 👨‍💻 Author

Ashwaz Poojary  
B.Sc. IT Graduate – Mumbai University  
Frontend + Backend Developer  
Strong focus on business-oriented solutions

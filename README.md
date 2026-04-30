# 💪 Fitness Tracker (Django)

A full-stack fitness tracking web application built using Django that helps users monitor their daily health activities, including food intake, workouts, and essential health metrics.

This project focuses on providing a clean user experience with a dynamic dashboard that updates in real time based on user inputs.

---

## 🚀 Key Features

- 🔐 Secure user authentication (Register/Login)
- 🍽️ Food tracking with calorie calculation
- 🏋️ Workout logging with estimated calories burned
- 📊 Daily health tracking:
  - Steps
  - Water intake
  - Sleep
  - Weight
- 🎯 Goal setting for personalized fitness targets
- 📈 Interactive dashboard with progress indicators and remaining values

---

## 🛠 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS (custom UI)
- **Database:** SQLite
- **APIs:** External APIs for food/workout data (where applicable)

---

## ⚙️ How to Run the Project

```bash
git clone https://github.com/yourusername/fitness-tracker-django.git
cd fitness-tracker-django

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # (Windows)

# Install dependencies
pip install -r requirements.txt

# Run server
python manage.py runserver

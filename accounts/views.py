from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import now
from django.shortcuts import render, redirect
from .forms import FoodForm
from .models import DailyStats
from .models import Food
from django.utils.timezone import localdate
import datetime

import requests
from django.conf import settings


from .models import UserProfile, Workout, DailyStats, Goal
from .forms import (
    RegisterForm,
    UserProfileForm,
    WorkoutForm,
    DailyStatsForm,
    GoalForm
)

# =========================
# AUTHENTICATION VIEWS
# =========================

def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid username or password ❌"

    return render(request, "accounts/login.html", {"error": error})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):
    today = localdate()

    # 🔥 DAILY STATS
    stats_today = DailyStats.objects.filter(
        user=request.user,
        date=today
    ).first()

    if stats_today:
        steps = stats_today.steps
        water = stats_today.water
        sleep = stats_today.sleep
        weight_today = stats_today.weight
        consumed = stats_today.calories_consumed
    else:
        steps = water = sleep = 0
        weight_today = None
        consumed = 0

    # 🔥 RECENT WORKOUTS (DB)
    recent_workouts = Workout.objects.filter(
        user=request.user,
        date=today
    ).order_by('-id')

    stats = DailyStats.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user)

    try:
        profile = UserProfile.objects.get(user=request.user)
        goal = Goal.objects.filter(user=request.user).last()

        if goal:
            current_weight = profile.weight
            goal_progress = goal.progress(current_weight)
        else:
            goal_progress = 0

        # 🔥 BMR + CALORIES
        bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + 5

        activity_map = {
            'sedentary': 1.2,
            'moderate': 1.55,
            'active': 1.725
        }

        tdee = bmr * activity_map.get(profile.activity_level, 1.2)

        if profile.goal == 'fat_loss':
            calories = tdee - 500
        elif profile.goal == 'muscle_gain':
            calories = tdee + 300
        else:
            calories = tdee

        # 🔥 MACROS
        protein = round(profile.weight * 2)
        fats = round((calories * 0.25) / 9)
        carbs = round((calories - (protein * 4 + fats * 9)) / 4)

        # 🔥 FOOD TODAY
        foods_today = Food.objects.filter(
            user=request.user,
            date=today
        )

        protein_consumed = sum((f.protein * f.quantity) / 100 for f in foods_today)
        carbs_consumed = sum((f.carbs * f.quantity) / 100 for f in foods_today)
        fats_consumed = sum((f.fats * f.quantity) / 100 for f in foods_today)

        protein_remaining = max(protein - protein_consumed, 0)
        carbs_remaining = max(carbs - carbs_consumed, 0)
        fats_remaining = max(fats - fats_consumed, 0)

        # 🔥 CALORIES REMAINING
        remaining = calories - consumed if calories else 0

        if remaining > 0:
            calorie_message = f"You can eat {round(remaining)} kcal more today 🍽️"
        elif remaining < 0:
            calorie_message = f"You exceeded your goal by {abs(round(remaining))} kcal ⚠️"
        else:
            calorie_message = "Perfect! You hit your calorie goal 🎯"


    except UserProfile.DoesNotExist:
        calories = protein = fats = carbs = None
        protein_remaining = carbs_remaining = fats_remaining = 0
        remaining = 0
        calorie_message = ""
        goal = None
        goal_progress = 0
        todays_workout = {"name": "No plan", "duration": ""}

    # 🔥 HISTORY FOOD
    selected_date = request.GET.get('date')

    if selected_date:
        foods = Food.objects.filter(user=request.user, date=selected_date).order_by('-id')
    else:
        foods = Food.objects.filter(user=request.user, date=today).order_by('-id')

    total_food_calories = sum(food.total_calories() for food in foods)

    stats_data = DailyStats.objects.filter(user=request.user).order_by('date')

    dates = [str(s.date) for s in stats_data]
    calories_data = [s.calories_consumed for s in stats_data]
    burned_data = [s.calories for s in stats_data]

    progress = (consumed / calories * 100) if calories else 0
    progress = max(0, min(progress, 100))

    return render(request, 'accounts/dashboard.html', {
        'recent_workouts': recent_workouts,
        'stats': stats_today,
        'goals': goals,
        'calories': round(calories) if calories else None,
        'protein': protein,
        'fats': fats,
        'carbs': carbs,
        'consumed': consumed,
        'remaining': remaining,
        'foods': foods,
        'total_food_calories': total_food_calories,
        'dates': dates,
        'calories_data': calories_data,
        'burned_data': burned_data,
        'progress': progress,
        'protein_remaining': round(protein_remaining),
        'carbs_remaining': round(carbs_remaining),
        'fats_remaining': round(fats_remaining),
        'calorie_message': calorie_message,
        'goal': goal,
        'goal_progress': goal_progress,
        'steps': steps,
        'water': water,
        'sleep': sleep,
        'weight_today': weight_today,
        'protein_consumed': round(protein_consumed, 1),
        'carbs_consumed': round(carbs_consumed, 1),
        'fats_consumed': round(fats_consumed, 1),
    })


# =========================
# PROFILE (NEW FEATURE)
# =========================

@login_required
def profile_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form})


# =========================
# WORKOUT
# =========================

@login_required
def add_workout(request):
    MET_VALUES = {
        "running": 9.8,
        "walking": 3.5,
        "cycling": 7.5,
        "gym": 6.0,
        "yoga": 3.0,
        "football": 8.0,
        "cricket": 5.0
    }

    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user

            # 🔥 AUTO CALCULATE CALORIES
            profile = request.user.userprofile
            weight = profile.weight

            workout_type = obj.workout_type.lower()
            duration = obj.duration_minutes

            met = MET_VALUES.get(workout_type, 5)

            calories_burned = (met * weight * 3.5 / 200) * duration

            obj.calories = round(calories_burned)
            obj.save()

            # 🔥 UPDATE DAILY STATS
            today = now().date()

            stats, _ = DailyStats.objects.get_or_create(
                user=request.user,
                date=today
            )

            stats.calories += obj.calories
            stats.save()

            return redirect('dashboard')
    else:
        form = WorkoutForm()

    return render(request, 'accounts/add_workout.html', {'form': form})

# =========================
# DELETE WORKOUT
# =========================

def delete_workout(request, id):
    workout = Workout.objects.get(id=id)

    if workout.user == request.user:
        workout.delete()

    return redirect('dashboard')

# =========================
# DAILY STATS
# =========================

@login_required
def add_stats(request):
    today = localdate()

    stats, _ = DailyStats.objects.get_or_create(
        user=request.user,
        date=today
    )

    if request.method == 'POST':
        form = DailyStatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DailyStatsForm(instance=stats)

    return render(request, 'accounts/add_stats.html', {
        'form': form
    })


# =========================
# GOALS
# =========================

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('dashboard')
    else:
        form = GoalForm()

    return render(request, 'accounts/add_goal.html', {'form': form})

# =========================
# ADD FOOD
# =========================

def add_food(request):
    food_options = []

    # 🔥 Protein calculation
    profile = request.user.userprofile
    protein_goal = profile.weight * 2

    today = now().date()

    foods_today = Food.objects.filter(
        user=request.user,
        date=today
    )

    consumed_protein = sum([
        (food.protein * food.quantity) / 100 for food in foods_today
    ])

    protein_remaining = max(protein_goal - consumed_protein, 0)
    protein_progress = min((consumed_protein / protein_goal) * 100, 100) if protein_goal else 0

    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = float(request.POST.get('quantity', 100))

        # 🔥 1️⃣ SAVE FOOD (MOST IMPORTANT)
        if request.POST.get('calories'):
            food = Food.objects.create(
                user=request.user,
                name=name,
                quantity=quantity,
                calories=float(request.POST.get('calories')),
                protein=float(request.POST.get('protein', 0)),
                carbs=float(request.POST.get('carbs', 0)),
                fats=float(request.POST.get('fats', 0)) 
            )

            stats, _ = DailyStats.objects.get_or_create(
                user=request.user,
                date=today
            )

            stats.calories_consumed += food.total_calories()
            stats.save()

            return redirect('dashboard')

        # 🍽️ 2️⃣ MEAL GENERATOR
        if request.POST.get('generate_meal'):
            meal_plan = []

            if protein_remaining > 40:
                meal_plan = [
                    {"name": "Chicken Breast (200g)", "protein": 40},
                    {"name": "Eggs (3)", "protein": 18}
                ]
            elif protein_remaining > 20:
                meal_plan = [
                    {"name": "Paneer (150g)", "protein": 25},
                    {"name": "Milk (1 glass)", "protein": 8}
                ]
            elif protein_remaining > 0:
                meal_plan = [
                    {"name": "Curd (100g)", "protein": 5},
                    {"name": "Almonds (10)", "protein": 3}
                ]

            return render(request, 'accounts/add_food.html', {
                'food_options': food_options,
                'protein_remaining': protein_remaining,
                'protein_progress': protein_progress,
                'meal_plan': meal_plan
            })

        # 🔥 3️⃣ API SEARCH
        url = "https://api.edamam.com/api/food-database/v2/parser"
        params = {
            "ingr": name,
            "app_id": settings.EDAMAM_APP_ID,
            "app_key": settings.EDAMAM_APP_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('hints'):
            for item in data['hints'][:5]:
                food_data = item['food']
                nutrients = food_data.get('nutrients', {})

                food_options.append({
                    'name': food_data['label'],
                    'calories': nutrients.get('ENERC_KCAL', 0),
                    'protein': nutrients.get('PROCNT', 0),
                    'carbs': nutrients.get('CHOCDF', 0),
                    'fats': nutrients.get('FAT', 0),
                    'protein_density': (
                        nutrients.get('PROCNT', 0) /
                        max(nutrients.get('ENERC_KCAL', 1), 1)
                    ) * 100
                })

            food_options = sorted(
                food_options,
                key=lambda x: x['protein_density'],
                reverse=True
            )

    return render(request, 'accounts/add_food.html', {
        'food_options': food_options,
        'protein_remaining': protein_remaining,
        'protein_progress': protein_progress
    })
# =========================
# DELETE FOOD
# =========================

def delete_food(request, food_id):
    food = Food.objects.get(id=food_id, user=request.user)
    
    # 🔥 subtract calories from stats
    today = now().date()
    stats = DailyStats.objects.filter(user=request.user, date=today).first()

    if stats:
       stats.calories_consumed -= food.total_calories()

    if stats.calories_consumed < 0:
        stats.calories_consumed = 0

    stats.save()

    food.delete()
    return redirect('dashboard')
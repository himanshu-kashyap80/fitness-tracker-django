# models.py placeholder

from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db import models

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    WORKOUT_CHOICES = [
        ('running', 'Running'),
        ('walking', 'Walking'),
        ('cycling', 'Cycling'),
        ('gym', 'Gym'),
        ('yoga', 'Yoga'),
        ('football', 'Football'),
        ('cricket', 'Cricket'),
    ]

    workout_type = models.CharField(max_length=50, choices=WORKOUT_CHOICES)
    duration_minutes = models.IntegerField()
    calories = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} on {self.date}"

class DailyStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=now)

    # 🔥 Health Tracking
    steps = models.IntegerField(default=0)
    water = models.FloatField(default=0)   # liters
    sleep = models.FloatField(default=0)   # hours
    weight = models.FloatField(null=True, blank=True)

    # 🎯 Goals (NEW)
    step_goal = models.IntegerField(default=10000)
    water_goal = models.FloatField(default=3.0)
    sleep_goal = models.FloatField(default=8.0)

    # 🔥 Calories
    calories = models.FloatField(default=0)  # burned
    calories_consumed = models.FloatField(default=0)

    # 🔥 Calculations (BEST PRACTICE)
    @property
    def steps_remaining(self):
        return max(self.step_goal - self.steps, 0)

    @property
    def water_remaining(self):
        return max(self.water_goal - self.water, 0)

    @property
    def sleep_remaining(self):
        return max(self.sleep_goal - self.sleep, 0)

    @property
    def steps_percent(self):
        return (self.steps / self.step_goal * 100) if self.step_goal else 0

    @property
    def water_percent(self):
        return (self.water / self.water_goal * 100) if self.water_goal else 0

    @property
    def sleep_percent(self):
        return (self.sleep / self.sleep_goal * 100) if self.sleep_goal else 0
    

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    
class Goal(models.Model):
    GOAL_CHOICES = [
        ('fat_loss', 'Fat Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=20, choices=GOAL_CHOICES)
    target_weight = models.FloatField(null=True, blank=True)
    start_weight = models.FloatField()
    created_at = models.DateField(auto_now_add=True)

    def progress(self, current_weight):
        if not self.target_weight:
            return 0
        total = abs(self.start_weight - self.target_weight)
        done = abs(self.start_weight - current_weight)
        return min((done / total) * 100, 100) if total else 0

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    
    GOAL_CHOICES = [
        ('fat_loss', 'Fat Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
    ]
    
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
    ]

    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)

    def __str__(self):
        return self.user.username
    
FOOD_CHOICES = [
    ('Rice', 'Rice'),
    ('Chicken Breast', 'Chicken Breast'),
    ('Egg', 'Egg'),
    ('Milk', 'Milk'),
    ('Banana', 'Banana'),
    ('Apple', 'Apple'),
    ('Bread', 'Bread'),
]
    
class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, choices=FOOD_CHOICES)

    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)

    quantity = models.FloatField(default=100)  # 🔥 NEW (grams)

    date = models.DateField(default=now)

    def total_calories(self):
        return (self.calories * self.quantity) / 100

    def __str__(self):
        return f"{self.name} ({self.quantity}g)"
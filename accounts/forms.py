from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Food

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']



from .models import Workout, DailyStats, Goal

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['workout_type', 'duration_minutes']

class DailyStatsForm(forms.ModelForm):
    class Meta:
        model = DailyStats
        fields = ['steps', 'water', 'sleep', 'weight']

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['goal_type', 'start_weight', 'target_weight']

from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'weight', 'height', 'goal', 'activity_level']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name','quantity']  

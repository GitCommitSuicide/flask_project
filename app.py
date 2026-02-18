from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
from models import init_db, User, Exercise, YogaPose, Meal, UserProgress, ExerciseLog, MealLog
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database setup
DATABASE_URL = 'sqlite:///fitness_app.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Initialize database
init_db()

# Helper function to get database session
def get_db_session():
  return Session()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
      username = request.form['username']
      email = request.form['email']
      password = request.form['password']
      height = float(request.form['height'])
      weight = float(request.form['weight'])
      goal = request.form['goal']
      
      db_session = get_db_session()
      
      # Check if user exists
      existing_user = db_session.query(User).filter_by(email=email).first()
      if existing_user:
          flash('Email already registered')
          db_session.close()
          return render_template('register.html')
      
      # Create new user
      hashed_password = generate_password_hash(password)
      new_user = User(
          username=username,
          email=email,
          password_hash=hashed_password,
          height=height,
          weight=weight,
          goal=goal
      )
      
      db_session.add(new_user)
      db_session.commit()
      db_session.close()
      
      flash('Registration successful! Please login.')
      return redirect(url_for('login'))
  
  return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      
      db_session = get_db_session()
      user = db_session.query(User).filter_by(email=email).first()
      
      if user and check_password_hash(user.password_hash, password):
          session['user_id'] = user.id
          session['username'] = user.username
          db_session.close()
          return redirect(url_for('dashboard'))
      else:
          flash('Invalid email or password')
          db_session.close()
  
  return render_template('login.html')

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  db_session = get_db_session()
  user = db_session.query(User).filter_by(id=session['user_id']).first()
  
  # Get recent progress
  recent_progress = db_session.query(UserProgress).filter_by(user_id=user.id).order_by(UserProgress.date.desc()).limit(7).all()
  
  # Calculate BMI
  bmi = user.weight / ((user.height / 100) ** 2)
  
  # Get today's logs
  today = datetime.now().date()
  today_exercises = db_session.query(ExerciseLog).filter_by(user_id=user.id, date=today).all()
  today_meals = db_session.query(MealLog).filter_by(user_id=user.id, date=today).all()
  
  # Calculate today's calories
  calories_burned = sum([log.calories_burned for log in today_exercises])
  calories_consumed = sum([log.calories for log in today_meals])
  
  db_session.close()
  
  return render_template('dashboard.html', 
                       user=user, 
                       bmi=round(bmi, 1),
                       recent_progress=recent_progress,
                       calories_burned=calories_burned,
                       calories_consumed=calories_consumed,
                       net_calories=calories_consumed - calories_burned)

@app.route('/update_progress', methods=['POST'])
def update_progress():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  weight = float(request.form['weight'])
  notes = request.form.get('notes', '')
  
  db_session = get_db_session()
  
  # Update user weight
  user = db_session.query(User).filter_by(id=session['user_id']).first()
  user.weight = weight
  
  # Add progress entry
  progress = UserProgress(
      user_id=session['user_id'],
      weight=weight,
      notes=notes,
      date=datetime.now().date()
  )
  
  db_session.add(progress)
  db_session.commit()
  db_session.close()
  
  flash('Progress updated successfully!')
  return redirect(url_for('dashboard'))

@app.route('/exercises')
def exercises():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  db_session = get_db_session()
  exercises = db_session.query(Exercise).all()
  
  # Group exercises by category
  exercise_categories = {}
  for exercise in exercises:
      if exercise.category not in exercise_categories:
          exercise_categories[exercise.category] = []
      exercise_categories[exercise.category].append(exercise)
  
  db_session.close()
  
  return render_template('exercises.html', exercise_categories=exercise_categories)

@app.route('/log_exercise', methods=['POST'])
def log_exercise():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  exercise_id = int(request.form['exercise_id'])
  duration = int(request.form['duration'])
  
  db_session = get_db_session()
  exercise = db_session.query(Exercise).filter_by(id=exercise_id).first()
  
  # Calculate calories burned (simplified calculation)
  calories_burned = (exercise.calories_per_minute * duration)
  
  exercise_log = ExerciseLog(
      user_id=session['user_id'],
      exercise_id=exercise_id,
      duration=duration,
      calories_burned=calories_burned,
      date=datetime.now().date()
  )
  
  db_session.add(exercise_log)
  db_session.commit()
  
  flash(f'Logged {exercise.name} for {duration} minutes!')
  db_session.close() # Moved this line here
  
  return redirect(url_for('exercises'))

@app.route('/yoga')
def yoga():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  db_session = get_db_session()
  yoga_poses = db_session.query(YogaPose).all()
  db_session.close()
  
  return render_template('yoga.html', yoga_poses=yoga_poses)

@app.route('/diet')
def diet():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  db_session = get_db_session()
  user = db_session.query(User).filter_by(id=session['user_id']).first()
  meals = db_session.query(Meal).all()
  
  # Group meals by category
  meal_categories = {}
  for meal in meals:
      if meal.category not in meal_categories:
          meal_categories[meal.category] = []
      meal_categories[meal.category].append(meal)
  
  db_session.close()
  
  return render_template('diet.html', meal_categories=meal_categories, user=user)

@app.route('/log_meal', methods=['POST'])
def log_meal():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  
  meal_id = int(request.form['meal_id'])
  quantity = float(request.form['quantity'])
  
  db_session = get_db_session()
  meal = db_session.query(Meal).filter_by(id=meal_id).first()
  
  # Calculate total calories
  total_calories = meal.calories * quantity
  
  meal_log = MealLog(
      user_id=session['user_id'],
      meal_id=meal_id,
      quantity=quantity,
      calories=total_calories,
      date=datetime.now().date()
  )
  
  db_session.add(meal_log)
  db_session.commit()
  
  flash(f'Logged {meal.name}!')
  db_session.close() # Moved this line here
  
  return redirect(url_for('diet'))

@app.route('/chatbot')
def chatbot():
  if 'user_id' not in session:
      return redirect(url_for('login'))
  return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
  if 'user_id' not in session:
      return jsonify({'error': 'Not logged in'})
  
  user_message = request.json.get('message', '').lower()
  
  # Simple chatbot responses
  responses = {
      'workout': "For a great workout, try combining 30 minutes of cardio with strength training. Check out our exercise section for specific routines!",
      'yoga': "Yoga is excellent for flexibility and mental health. Start with basic poses like Downward Dog and Mountain Pose. Visit our yoga section for more!",
      'diet': "A balanced diet includes proteins, carbs, and healthy fats. Check our diet section for meal plans based on your goals!",
      'weight loss': "For weight loss, maintain a caloric deficit by eating fewer calories than you burn. Combine cardio with strength training!",
      'weight gain': "For weight gain, eat in a caloric surplus with protein-rich foods. Focus on strength training to build muscle mass.",
      'bmi': "BMI is calculated as weight(kg) / height(m)². A healthy BMI is typically between 18.5-24.9.",
      'calories': "Daily calorie needs vary by age, gender, and activity level. Generally 2000-2500 for adults. Track your intake in our diet section!",
      'exercise': "Regular exercise should include cardio, strength training, and flexibility work. Aim for at least 150 minutes of moderate activity per week."
  }
  
  # Find matching response
  response = "I'm here to help with fitness, nutrition, and wellness questions! Try asking about workouts, yoga, diet, or weight management."
  
  for keyword, reply in responses.items():
      if keyword in user_message:
          response = reply
          break
  
  return jsonify({'response': response})

@app.route('/progress_data')
def progress_data():
  if 'user_id' not in session:
      return jsonify({'error': 'Not logged in'})
  
  db_session = get_db_session()
  progress = db_session.query(UserProgress).filter_by(user_id=session['user_id']).order_by(UserProgress.date).limit(30).all()
  
  data = {
      'dates': [p.date.strftime('%Y-%m-%d') for p in progress],
      'weights': [p.weight for p in progress]
  }
  
  db_session.close()
  return jsonify(data)

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

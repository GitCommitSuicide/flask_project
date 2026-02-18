from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(120), nullable=False)
    height = Column(Float, nullable=False)  # in cm
    weight = Column(Float, nullable=False)  # in kg
    goal = Column(String(50), nullable=False)  # lose_weight, gain_weight, maintain_weight
    created_at = Column(Date, default=datetime.now().date())
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user")
    exercise_logs = relationship("ExerciseLog", back_populates="user")
    meal_logs = relationship("MealLog", back_populates="user")

class Exercise(Base):
    __tablename__ = 'exercises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # strength, cardio, flexibility, yoga, bodyweight
    description = Column(Text)
    calories_per_minute = Column(Float, nullable=False)
    image_url = Column(String(200), default='exercise_placeholder.jpg')
    
    # Relationships
    exercise_logs = relationship("ExerciseLog", back_populates="exercise")

class YogaPose(Base):
    __tablename__ = 'yoga_poses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    benefits = Column(Text)
    hold_time = Column(Integer)  # in seconds
    calories_burned = Column(Float)
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    image_url = Column(String(200), default='yoga_placeholder.jpg')

class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    calories = Column(Float, nullable=False)  # per serving
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fats = Column(Float, default=0)
    is_vegetarian = Column(Integer, default=0)  # 0 = no, 1 = yes
    
    # Relationships
    meal_logs = relationship("MealLog", back_populates="meal")

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    weight = Column(Float, nullable=False)
    notes = Column(Text)
    date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="progress")

class ExerciseLog(Base):
    __tablename__ = 'exercise_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    calories_burned = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="exercise_logs")
    exercise = relationship("Exercise", back_populates="exercise_logs")

class MealLog(Base):
    __tablename__ = 'meal_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    meal_id = Column(Integer, ForeignKey('meals.id'), nullable=False)
    quantity = Column(Float, nullable=False)  # serving size
    calories = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="meal_logs")
    meal = relationship("Meal", back_populates="meal_logs")

def init_db():
    engine = create_engine('sqlite:///fitness_app.db')
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add sample exercises if table is empty
    if session.query(Exercise).count() == 0:
        exercises = [
            # Strength
            Exercise(name="Push-ups", category="strength", description="Classic upper body exercise", calories_per_minute=8, image_url="pushup.jpg"),
            Exercise(name="Pull-ups", category="strength", description="Upper body pulling exercise", calories_per_minute=10, image_url="pullup.jpg"),
            Exercise(name="Squats", category="strength", description="Lower body compound exercise", calories_per_minute=7, image_url="squat.jpg"),
            Exercise(name="Deadlifts", category="strength", description="Full body compound exercise", calories_per_minute=12, image_url="deadlift.jpg"),
            Exercise(name="Bench Press", category="strength", description="Chest and tricep exercise", calories_per_minute=9, image_url="benchpress.jpg"),
            
            # Cardio
            Exercise(name="Running", category="cardio", description="High intensity cardio", calories_per_minute=15, image_url="running.jpg"),
            Exercise(name="Cycling", category="cardio", description="Low impact cardio", calories_per_minute=12, image_url="cycling.jpg"),
            Exercise(name="Swimming", category="cardio", description="Full body cardio", calories_per_minute=14, image_url="swimming.jpg"),
            Exercise(name="Jumping Jacks", category="cardio", description="Quick cardio exercise", calories_per_minute=10, image_url="jumpingjacks.jpg"),
            Exercise(name="Burpees", category="cardio", description="High intensity full body", calories_per_minute=16, image_url="burpees.jpg"),
            
            # Bodyweight
            Exercise(name="Planks", category="bodyweight", description="Core strengthening", calories_per_minute=5, image_url="plank.jpg"),
            Exercise(name="Mountain Climbers", category="bodyweight", description="Cardio and core", calories_per_minute=11, image_url="mountainclimbers.jpg"),
            Exercise(name="Lunges", category="bodyweight", description="Lower body exercise", calories_per_minute=6, image_url="lunges.jpg"),
            Exercise(name="Crunches", category="bodyweight", description="Abdominal exercise", calories_per_minute=4, image_url="crunches.jpg"),
            Exercise(name="Dips", category="bodyweight", description="Tricep exercise", calories_per_minute=7, image_url="dips.jpg"),
        ]
        
        for exercise in exercises:
            session.add(exercise)
    
    # Add sample yoga poses
    if session.query(YogaPose).count() == 0:
        yoga_poses = [
            YogaPose(name="Downward Dog", benefits="Stretches hamstrings and calves", hold_time=60, calories_burned=3, difficulty="beginner"),
            YogaPose(name="Warrior I", benefits="Strengthens legs and core", hold_time=45, calories_burned=4, difficulty="beginner"),
            YogaPose(name="Tree Pose", benefits="Improves balance and focus", hold_time=30, calories_burned=2, difficulty="beginner"),
            YogaPose(name="Child's Pose", benefits="Relaxes back and shoulders", hold_time=90, calories_burned=1, difficulty="beginner"),
            YogaPose(name="Cobra Pose", benefits="Strengthens back muscles", hold_time=30, calories_burned=3, difficulty="intermediate"),
            YogaPose(name="Triangle Pose", benefits="Stretches sides and legs", hold_time=45, calories_burned=3, difficulty="intermediate"),
            YogaPose(name="Pigeon Pose", benefits="Opens hips and stretches", hold_time=60, calories_burned=2, difficulty="intermediate"),
            YogaPose(name="Crow Pose", benefits="Builds arm and core strength", hold_time=20, calories_burned=5, difficulty="advanced"),
        ]
        
        for pose in yoga_poses:
            session.add(pose)
    
    # Add sample meals
    if session.query(Meal).count() == 0:
        meals = [
            # Breakfast
            Meal(name="Oatmeal with Berries", category="breakfast", calories=250, protein=8, carbs=45, fats=4, is_vegetarian=1),
            Meal(name="Scrambled Eggs", category="breakfast", calories=200, protein=14, carbs=2, fats=14, is_vegetarian=0),
            Meal(name="Greek Yogurt", category="breakfast", calories=150, protein=15, carbs=12, fats=0, is_vegetarian=1),
            Meal(name="Avocado Toast", category="breakfast", calories=300, protein=8, carbs=30, fats=18, is_vegetarian=1),
            
            # Lunch
            Meal(name="Grilled Chicken Salad", category="lunch", calories=350, protein=30, carbs=15, fats=18, is_vegetarian=0),
            Meal(name="Quinoa Bowl", category="lunch", calories=400, protein=12, carbs=60, fats=12, is_vegetarian=1),
            Meal(name="Tuna Sandwich", category="lunch", calories=320, protein=25, carbs=35, fats=8, is_vegetarian=0),
            Meal(name="Vegetable Soup", category="lunch", calories=180, protein=6, carbs=25, fats=5, is_vegetarian=1),
            
            # Dinner
            Meal(name="Grilled Salmon", category="dinner", calories=400, protein=35, carbs=0, fats=25, is_vegetarian=0),
            Meal(name="Chicken Breast", category="dinner", calories=300, protein=40, carbs=0, fats=8, is_vegetarian=0),
            Meal(name="Lentil Curry", category="dinner", calories=350, protein=18, carbs=45, fats=8, is_vegetarian=1),
            Meal(name="Stir-fried Vegetables", category="dinner", calories=200, protein=8, carbs=25, fats=8, is_vegetarian=1),
            
            # Snacks
            Meal(name="Apple", category="snack", calories=80, protein=0, carbs=20, fats=0, is_vegetarian=1),
            Meal(name="Almonds (1 oz)", category="snack", calories=160, protein=6, carbs=6, fats=14, is_vegetarian=1),
            Meal(name="Protein Shake", category="snack", calories=120, protein=25, carbs=3, fats=1, is_vegetarian=1),
            Meal(name="Banana", category="snack", calories=100, protein=1, carbs=25, fats=0, is_vegetarian=1),
        ]
        
        for meal in meals:
            session.add(meal)
    
    session.commit()
    session.close()

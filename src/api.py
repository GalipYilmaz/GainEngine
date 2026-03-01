from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any
from src.data_manager import DataManager
from src.workout_engine import WorkoutEngine

# Create the FastAPI application instance
app = FastAPI(title="GainEngine API")

# Initialize the data manager and workout engine
data_manager = DataManager()
workout_engine = WorkoutEngine(data_manager)

# Load the pre-trained ML similarity model on startup
workout_engine.load_model()

# Mount the static directory to serve CSS and JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the directory where HTML templates are stored
templates = Jinja2Templates(directory="templates")


# Model for weekly workout generation requests
class WorkoutRequest(BaseModel):
    split_name: str
    equipment_profile: str  # Updated from List[str] to str
    volume_level: str = "Normal"


# Model for smart exercise swap requests (ML-based)
class SwapRequest(BaseModel):
    exercise_name: str
    equipment_profile: str  # Updated from List[str] to str
    current_day_exercises: List[str] = []


# Helper function to convert the selected profile into a list of equipment
def get_equipment_list(profile: str) -> List[str]:
    all_eq = data_manager.get_unique_equipment()
    if profile == "Bodyweight":
        return ["body weight", "assisted"]
    elif profile == "Home Gym":
        return ["body weight", "assisted", "dumbbell", "band", "kettlebell", "medicine ball", "stability ball"]
    else:
        # Commercial Gym has access to everything
        return all_eq


# Root endpoint to serve the frontend HTML page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Endpoint to provide dropdown options (Splits and Volumes)
@app.get("/options")
def get_options():
    return {
        "splits": list(workout_engine.splits.keys()),
        "volumes": ["Low", "Normal", "High"]
        # Equipment list is no longer sent to the frontend since we use profiles
    }


# Endpoint to generate the full weekly workout plan
@app.post("/generate")
def generate_workout_endpoint(request: WorkoutRequest):
    # Convert the profile string back to a list of valid equipment
    eq_list = get_equipment_list(request.equipment_profile)

    weekly_plan = workout_engine.generate_workout_plan(
        split_name=request.split_name,
        equipment_list=eq_list,
        volume_level=request.volume_level
    )

    if not weekly_plan:
        raise HTTPException(
            status_code=404,
            detail="Could not generate a plan with the given criteria."
        )

    return weekly_plan


# Endpoint to find a mathematically similar exercise using Cosine Similarity
@app.post("/swap")
def swap_exercise_endpoint(request: SwapRequest):
    # Convert the profile string back to a list of valid equipment
    eq_list = get_equipment_list(request.equipment_profile)

    alternative = workout_engine.get_smart_alternative(
        exercise_name=request.exercise_name,
        equipment_list=eq_list,
        current_exercises=request.current_day_exercises  # Prevents duplicate recommendations
    )

    if not alternative:
        raise HTTPException(status_code=404, detail="No suitable alternative found.")

    return alternative
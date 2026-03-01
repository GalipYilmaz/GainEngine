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

# Mount the static directory to serve CSS and JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the directory where HTML templates are stored
templates = Jinja2Templates(directory="templates")


# Updated request model for Weekly Split and Volume
class WorkoutRequest(BaseModel):
    split_name: str
    equipment_list: List[str]
    volume_level: str = "Normal"


# Root endpoint to serve the frontend HTML page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Endpoint to provide dropdown options (Splits and Equipment)
@app.get("/options")
def get_options():
    return {
        "splits": list(workout_engine.splits.keys()),
        "equipment": data_manager.get_unique_equipment(),
        "volumes": ["Low", "Normal", "High"]
    }


# Endpoint to generate the weekly workout plan
@app.post("/generate")
def generate_workout_endpoint(request: WorkoutRequest):
    # The engine now returns a dictionary of days
    weekly_plan = workout_engine.generate_workout_plan(
        split_name=request.split_name,
        equipment_list=request.equipment_list,
        volume_level=request.volume_level
    )

    if not weekly_plan:
        raise HTTPException(
            status_code=404,
            detail="Could not generate a plan with the given criteria."
        )

    return weekly_plan
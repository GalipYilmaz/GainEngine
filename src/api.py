from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
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

# Define the structure of the incoming request
class WorkoutRequest(BaseModel):
    body_part: str
    equipment_list: List[str]
    num_exercises: int = 5

# Root endpoint to serve the frontend HTML page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to provide dropdown options for the user interface
@app.get("/options")
def get_options():
    return {
        "body_parts": data_manager.get_unique_body_parts(),
        "equipment": data_manager.get_unique_equipment()
    }

# Endpoint to generate the actual workout
@app.post("/generate")
def generate_workout_endpoint(request: WorkoutRequest):
    workout_df = workout_engine.generate_workout(
        body_part=request.body_part,
        equipment_list=request.equipment_list,
        num_exercises=request.num_exercises
    )
    
    if workout_df is None or workout_df.empty:
        raise HTTPException(
            status_code=404, 
            detail="No exercises found for the given criteria."
        )
        
    return workout_df.to_dict(orient="records")

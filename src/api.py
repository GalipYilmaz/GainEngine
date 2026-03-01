from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from src.data_manager import DataManager
from src.workout_engine import WorkoutEngine

app = FastAPI(title="GainEngine API")

data_manager = DataManager()
workout_engine = WorkoutEngine(data_manager)

class WorkoutRequest(BaseModel):
    body_part: str
    equipment_list: List[str]
    num_exercises: int = 5

@app.get("/")
def read_root():
    return {"message": "Welcome to GainEngine API! The engine is running."}

@app.get("/options")
def get_options():
    return {
        "body_parts": data_manager.get_unique_body_parts(),
        "equipment": data_manager.get_unique_equipment()
    }

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
import pandas as pd
from data_manager import DataManager
from workout_engine import WorkoutEngine


def test_engine():
    print("Testing")

    # Initialize core components
    data_manager = DataManager()
    workout_engine = WorkoutEngine(data_manager)

    # Mock parameters for the test
    target_body_part = "Chest"
    available_equipment = ["barbell", "dumbbell", "body weight"]
    num_exercises = 4

    print(f"\nSelected Body Part: {target_body_part.title()}")
    print(f"Selected Equipment: {available_equipment}")
    print(f"Number of Exercises: {num_exercises}\n")

    split_name = f"Single: {target_body_part}"

    # Generate the workout plan
    weekly_plan = workout_engine.generate_workout_plan(
        split_name=split_name,
        equipment_list=available_equipment,
        volume_level="Low"
    )

    # Fetch the specific day's list
    workout_list = weekly_plan.get(target_body_part, [])

    if not workout_list or isinstance(workout_list, str):
        workout = pd.DataFrame()
    else:
        # Convert to DataFrame and clean up columns
        workout = pd.DataFrame(workout_list)
        if "type" in workout.columns:
            workout = workout.rename(columns={"type": "exercise_type"})

        # Limit to requested number of exercises
        workout = workout.head(num_exercises)

    if workout.empty:
        print("No workouts available")
    else:
        print("--------Workout---------")

        # Safely display target columns
        try:
            print(workout[["name", "equipment", "exercise_type"]])
        except KeyError:
            print(workout)

        print("\nTest completed")


if __name__ == "__main__":
    test_engine()
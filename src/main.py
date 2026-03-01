from data_manager import DataManager
from workout_engine import WorkoutEngine

def test_engine():
    print("Testing")

    data_manager = DataManager()
    workout_engine = WorkoutEngine(data_manager)

    target_body_part = "chest"
    available_equipment = ["barbell", "dumbbell", "body weight"]
    num_exercises = 4

    print(f"\nSelected Body Part: {target_body_part.title()}")
    print(f"Selected Equipment: {available_equipment}")
    print(f"Number of Exercises: {num_exercises}\n")

    workout = workout_engine.generate_workout(
        target_body_part,
        available_equipment,
        num_exercises
    )

    if workout is None or workout.empty:
        print("No workouts available")
    else:
        print("--------Workout---------")

        try:
            print(workout[["name", "equipment", "exercise_type"]])
        except KeyError:
            print(workout)

        print("Test completed")

if __name__ == "__main__":
    test_engine()
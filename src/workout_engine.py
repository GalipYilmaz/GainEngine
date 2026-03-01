import pandas as pd
import random


class WorkoutEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # Define workout split templates
        self.splits = {
            "Fullbody 3 Day": ["Full Body", "Rest", "Full Body", "Rest", "Full Body", "Rest", "Rest"],
            "Upper Lower 4 Day": ["Upper", "Lower", "Rest", "Upper", "Lower", "Rest", "Rest"],
            "PPL 6 Day": ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Rest"],
            "Bro Split 5 Day": ["Chest", "Back", "Shoulders", "Legs", "Arms", "Rest", "Rest"],
            "PPL Fullbody 4 Day": ["Push", "Pull", "Legs", "Rest", "Full Body", "Rest", "Rest"]
        }

    def get_split_days(self, split_name):
        return self.splits.get(split_name, [])

    def generate_workout_plan(self, split_name, equipment_list, volume_level="Normal"):
        """Generates a full weekly workout plan based on split and volume level."""
        df = self.data_manager.get_data()
        days = self.get_split_days(split_name)

        # Volume settings: (sets, reps)
        # Low: 2-3 sets, High: 4-5 sets
        vol_config = {
            "Low": {"Compound": "2x8-10", "Isolation": "2x12-15", "num": 4},
            "Normal": {"Compound": "3x8-10", "Isolation": "3x12-15", "num": 6},
            "High": {"Compound": "4x6-8", "Isolation": "4x12-15", "num": 8}
        }

        config = vol_config.get(volume_level, vol_config["Normal"])
        weekly_plan = {}

        for i, target in enumerate(days):
            day_name = f"Day {i + 1} - {target}"
            if target == "Rest":
                weekly_plan[day_name] = "Rest Day - Recovery is key!"
                continue

            # Filter exercises based on day's target and equipment
            day_exercises = self._filter_by_split_type(df, target, equipment_list)

            if day_exercises.empty:
                weekly_plan[day_name] = "No exercises found for these criteria."
                continue

            # Select workout based on volume number
            sample_size = min(len(day_exercises), config["num"])
            selected = day_exercises.sample(n=sample_size)

            # Add volume info (sets/reps) to each exercise
            final_list = []
            for _, row in selected.iterrows():
                v_info = config["Compound"] if row.get("exercise_type") == "Compound" else config["Isolation"]
                final_list.append({
                    "name": row["name"],
                    "equipment": row["equipment"],
                    "type": row.get("exercise_type", "N/A"),
                    "volume": v_info
                })

            weekly_plan[day_name] = final_list

        return weekly_plan

    def _filter_by_split_type(self, df, target, equipment_list):
        """Helper to map split targets (Push/Pull/Upper) to actual body parts."""
        mapping = {
            "Push": ["chest", "shoulders", "triceps"],
            "Pull": ["back", "biceps"],
            "Legs": ["quads", "hamstrings", "calves", "glutes"],
            "Upper": ["chest", "back", "shoulders", "triceps", "biceps"],
            "Lower": ["quads", "hamstrings", "calves", "glutes"],
            "Full Body": ["chest", "back", "legs", "shoulders", "triceps", "biceps"]
        }

        target_parts = mapping.get(target, [target.lower()])
        return df[(df["bodyPart"].isin(target_parts)) & (df["equipment"].isin(equipment_list))]
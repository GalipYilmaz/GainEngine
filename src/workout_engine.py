import pandas as pd
import random
import pickle


class WorkoutEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # 1. Removed Single sessions, keeping only Weekly Splits
        self.splits = {
            "Fullbody 3 Day": ["Full Body", "Rest", "Full Body", "Rest", "Full Body", "Rest", "Rest"],
            "Upper Lower 4 Day": ["Upper", "Lower", "Rest", "Upper", "Lower", "Rest", "Rest"],
            "PPL 6 Day": ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Rest"],
            "Bro Split 5 Day": ["Chest", "Back", "Shoulders", "Legs", "Arms", "Rest", "Rest"],
            "PPL Fullbody 4 Day": ["Push", "Pull", "Legs", "Rest", "Full Body", "Rest", "Rest"]
        }

        # 2. Fixed Exercise Blueprints (Diversity and Order)
        # Defines exactly how many exercises per muscle group for each day type.
        # Order matters: Large muscle groups are targeted before smaller ones.
        self.blueprints = {
            "Full Body": {"chest": 2, "back": 2, "legs": 2, "shoulders": 1, "triceps": 1, "biceps": 1},  # Total: 9
            "Upper": {"chest": 2, "back": 2, "shoulders": 2, "triceps": 1, "biceps": 1},  # Total: 8
            "Lower": {"legs": 4, "calves": 2},  # Total: 6
            "Push": {"chest": 3, "shoulders": 2, "triceps": 2},  # Total: 7
            "Pull": {"back": 4, "biceps": 2},  # Total: 6
            "Legs": {"legs": 4, "calves": 2},  # Total: 6
            "Chest": {"chest": 5},
            "Back": {"back": 5},
            "Shoulders": {"shoulders": 5},
            "Arms": {"triceps": 3, "biceps": 3}
        }

    def load_model(self):
        """Loads the pre-trained ML similarity model from the pickle file."""
        try:
            with open("data/similarity_model.pkl", "rb") as f:
                self.model_data = pickle.load(f)
            print("🚀 ML Model loaded successfully.")
        except FileNotFoundError:
            print("⚠️ Model file not found! Run ml_trainer.py first.")

    def generate_workout_plan(self, split_name, equipment_list, volume_level="Normal"):
        """Generates a structured weekly plan using fixed blueprints."""
        df = self.data_manager.get_data()
        days = self.splits.get(split_name, [])

        # Volume level now strictly controls Sets/Reps, not exercise count
        vol_config = {
            "Low": {"Compound": "2x8-10", "Isolation": "2x12-15"},
            "Normal": {"Compound": "3x8-10", "Isolation": "3x12-15"},
            "High": {"Compound": "4x6-8", "Isolation": "4x12-15"}
        }
        config = vol_config.get(volume_level, vol_config["Normal"])
        weekly_plan = {}

        for i, day_type in enumerate(days):
            day_label = f"Day {i + 1} - {day_type}"

            if day_type == "Rest":
                weekly_plan[day_label] = "Rest Day - Recovery is key!"
                continue

            # Fetch the specific blueprint for this day
            blueprint = self.blueprints.get(day_type, {})
            final_list = []

            # Iterate over the required muscle groups in the blueprint
            for muscle_group, count in blueprint.items():
                group_df = self._get_exercises_for_group(df, muscle_group, equipment_list)

                if not group_df.empty:
                    # Sample the exact amount, or whatever is available if less
                    sample_size = min(len(group_df), count)
                    selected = group_df.sample(n=sample_size)

                    for _, row in selected.iterrows():
                        v_info = config["Compound"] if row.get("exercise_type") == "Compound" else config["Isolation"]
                        final_list.append({
                            "name": row["name"],
                            "target": row["target"].capitalize() if pd.notna(row["target"]) else "N/A",
                            "equipment": row["equipment"],
                            "type": row.get("exercise_type", "N/A"),
                            "volume": v_info
                        })

            if not final_list:
                weekly_plan[day_label] = "No exercises found for this day's blueprint."
            else:
                weekly_plan[day_label] = final_list

        return weekly_plan

    def _get_exercises_for_group(self, df, group, equipment_list):
        """Maps blueprint muscle groups to the actual dataset columns."""
        mapping = {
            "chest": ["chest", "pectorals"],
            "back": ["back", "lats", "traps", "rhomboids"],
            "shoulders": ["shoulders", "delts"],
            "legs": ["upper legs", "quads", "hamstrings", "glutes"],
            "calves": ["lower legs", "calves"],
            "triceps": ["triceps"],
            "biceps": ["biceps"]
        }
        targets = mapping.get(group, [group.lower()])
        condition = (df["bodyPart"].str.lower().isin(targets)) | (df["target"].str.lower().isin(targets))
        return df[condition & (df["equipment"].isin(equipment_list))]

    def get_smart_alternative(self, exercise_name, equipment_list, current_exercises):
        """Finds the mathematically most similar alternative using Cosine Similarity."""
        if not hasattr(self, 'model_data'):
            return None

        sim_matrix = self.model_data["similarity_matrix"]
        names = self.model_data["exercise_names"]
        df = self.model_data["df"]

        if exercise_name not in names:
            return None

        # Get the index and full details of the original exercise
        idx = names.index(exercise_name)
        orig_exercise = df.iloc[idx]

        sim_scores = list(enumerate(sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        for i, score in sim_scores[1:]:
            alt_exercise = df.iloc[i]

            # 1. Does the equipment match the user's selected profile?
            if alt_exercise['equipment'] in equipment_list:
                # 2. Ensure the exercise is not the same as the original and not already in the current day's list
                if alt_exercise['name'] != exercise_name and alt_exercise['name'] not in current_exercises:
                    # 3. CRITICAL FILTER: Does it target the exact same body part as the original exercise?
                    if alt_exercise['bodyPart'] == orig_exercise['bodyPart']:
                        return alt_exercise.to_dict()

        return None
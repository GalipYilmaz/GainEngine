import pandas as pd
import random
import pickle


class WorkoutEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # 1. Weekly Splits (Only Weekly Plans)
        self.splits = {
            "Fullbody 3 Day": ["Full Body", "Rest", "Full Body", "Rest", "Full Body", "Rest", "Rest"],
            "Upper Lower 4 Day": ["Upper", "Lower", "Rest", "Upper", "Lower", "Rest", "Rest"],
            "PPL 6 Day": ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Rest"],
            "Bro Split 5 Day": ["Chest", "Back", "Shoulders", "Legs", "Arms", "Rest", "Rest"]
        }

        # 2. Perfected Blueprints (Optimized for Major vs Minor frequency)
        self.blueprints = {
            "Full Body": {"chest": 1, "back": 1, "legs": 1, "shoulders": 1, "triceps": 1, "biceps": 1},
            "Upper": {"chest": 2, "back": 2, "shoulders": 1, "triceps": 1, "biceps": 1},
            "Lower": {"legs": 3, "calves": 1},
            "Push": {"chest": 2, "shoulders": 1, "triceps": 1},
            "Pull": {"back": 2, "biceps": 1},
            "Legs": {"legs": 2, "calves": 1},
            "Chest": {"chest": 4},
            "Back": {"back": 4},
            "Shoulders": {"shoulders": 3},
            "Arms": {"triceps": 2, "biceps": 2}
        }

    def load_model(self):
        """Loads the pre-trained ML similarity model."""
        try:
            with open("data/similarity_model.pkl", "rb") as f:
                self.model_data = pickle.load(f)
            print("🚀 ML Model loaded successfully.")
        except FileNotFoundError:
            print("⚠️ Model file not found!")

    def generate_workout_plan(self, split_name, equipment_list, volume_level="Low"):
        """Generates a structured plan prioritizing Major vs Minor muscle group volumes."""
        df = self.data_manager.get_data()
        days = self.splits.get(split_name, [])

        vol_config = {
            "Low": {
                "Major": {"sets": 3, "reps": "8-10"},
                "Minor": {"sets": 2, "reps": "10-12"}
            },
            "High": {
                "Major": {"sets": 4, "reps": "8-10"},
                "Minor": {"sets": 3, "reps": "10-12"}
            }
        }
        config = vol_config.get(volume_level, vol_config["Low"])

        major_groups = ["chest", "back", "legs", "shoulders"]
        weekly_plan = {}

        for i, day_type in enumerate(days):
            day_label = f"Day {i + 1} - {day_type}"

            if day_type == "Rest":
                weekly_plan[day_label] = "Rest Day - Focus on recovery."
                continue

            blueprint = self.blueprints.get(day_type, {})
            final_list = []

            for muscle_group, count in blueprint.items():
                group_df = self._get_exercises_for_group(df, muscle_group, equipment_list)

                if not group_df.empty:
                    available = len(group_df)
                    num_to_select = min(available, count)
                    selected_exercises = group_df.sample(n=num_to_select)

                    volume_multiplier = count / num_to_select

                    group_type = "Major" if muscle_group in major_groups else "Minor"
                    base_sets = config[group_type]["sets"]
                    reps = config[group_type]["reps"]

                    adjusted_sets = int(base_sets * volume_multiplier)

                    for _, row in selected_exercises.iterrows():
                        final_list.append({
                            "name": row["name"],
                            "target": row["target"].capitalize() if pd.notna(row["target"]) else "N/A",
                            # İŞTE KRİTİK ÇÖZÜM: KAS GRUBUNU KESİN OLARAK ETİKETLİYORUZ!
                            "muscle_group": muscle_group.capitalize(),
                            "equipment": row["equipment"],
                            "type": row.get("exercise_type", "Compound"),
                            "volume": f"{adjusted_sets}x{reps}"
                        })

            weekly_plan[day_label] = final_list

        return weekly_plan

    def _get_exercises_for_group(self, df, group, equipment_list):
        """Maps blueprint muscle groups to the actual dataset columns with bulletproof filtering."""
        # Using word roots to catch variations like "pectorals" or "pectoral"
        mapping = {
            "chest": ["chest", "pectoral"],
            "back": ["back", "lat", "trap", "rhomboid"],
            "shoulders": ["shoulder", "delt"],
            "legs": ["leg", "quad", "hamstring", "glute"],
            "calves": ["calf", "calves", "lower leg"],
            "triceps": ["tricep", "upper arm"],
            "biceps": ["bicep", "upper arm"]
        }
        targets = mapping.get(group, [group.lower()])

        # 1. Bulletproof Cleanup: Replace NaN with empty string, convert all to lowercase
        body_parts = df["bodyPart"].fillna("").astype(str).str.lower()
        target_parts = df["target"].fillna("").astype(str).str.lower()

        # 2. Search using 'contains' logic instead of exact match ('isin')
        condition = pd.Series([False] * len(df), index=df.index)
        for t in targets:
            condition = condition | body_parts.str.contains(t, na=False) | target_parts.str.contains(t, na=False)

        filtered_df = df[condition & (df["equipment"].isin(equipment_list))]

        # TERMINAL DEBUGGER: Logs the number of exercises found for each muscle group
        print(f"🛠️ [DEBUG] Number of exercises found for {group.upper()} after equipment filter: {len(filtered_df)}")

        return filtered_df

    def get_smart_alternative(self, exercise_name, equipment_list, current_exercises):
        """Finds a mathematically similar alternative for the same body part."""
        if not hasattr(self, 'model_data'):
            return None

        sim_matrix = self.model_data["similarity_matrix"]
        names = self.model_data["exercise_names"]
        df = self.model_data["df"]

        if exercise_name not in names:
            return None

        idx = names.index(exercise_name)
        orig_exercise = df.iloc[idx]

        sim_scores = list(enumerate(sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        for i, score in sim_scores[1:]:
            alt_exercise = df.iloc[i]
            if alt_exercise['equipment'] in equipment_list:
                if alt_exercise['name'] != exercise_name and alt_exercise['name'] not in current_exercises:
                    if alt_exercise['bodyPart'] == orig_exercise['bodyPart']:
                        return alt_exercise.to_dict()
        return None
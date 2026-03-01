import pandas as pd

class WorkoutEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def generate_workout(self, body_part, equipment_list, num_exercises=5):
        """
            Generates a workout plan based on the target body part and available equipment.
            Attempts to balance compound and isolation exercises if the data is available.
        """
        df = self.data_manager.get_data()

        available_exercises = df[
            (df["bodyPart"] == body_part) &
            (df["equipment"].isin(equipment_list))
        ]

        if len(available_exercises) == 0:
            return None

        if len(available_exercises) <= num_exercises:
            return available_exercises

        if "exercise_type" in available_exercises.columns:
            # Separate the available exercises into compound and isolation groups
            compounds = available_exercises[available_exercises["exercise_type"] == "Compound"]
            isolations = available_exercises[available_exercises["exercise_type"] == "Isolation"]

            # Calculate target counts: aim for at least half to be compound exercises
            target_compounds = max(1, num_exercises // 2)
            target_isolation = num_exercises - target_compounds

            # Logic to handle cases where there aren't enough exercises in one of the categories
            if len(compounds) < target_compounds:
                final_compounds = compounds
                final_isolations = isolations.sample(n=min(len(isolations), num_exercises - len(compounds)))
            elif len(isolations) < target_isolation:
                final_isolations = isolations
                final_compounds = compounds.sample(n=min(len(compounds), num_exercises - len(isolations)))
            else:
                final_compounds = compounds.sample(n=target_compounds)
                final_isolations = isolations.sample(n=target_isolation)

            workout = pd.concat([final_compounds, final_isolations])
        else:
            # Fallback if there is no 'exercise_type' column: just pick random exercises
            workout = available_exercises.sample(n=num_exercises)

        # Shuffle the final workout list and reset the index for a clean dataframe
        return workout.sample(frac=1).reset_index(drop=True)
import matplotlib.pyplot as plt
import io
import base64


class WorkoutVisualizer:
    def __init__(self):
        # Map specific targets to general muscle groups for the chart
        self.group_mapping = {
            "chest": "Chest", "pectorals": "Chest",
            "back": "Back", "lats": "Back", "traps": "Back", "rhomboids": "Back",
            "shoulders": "Shoulders", "delts": "Shoulders",
            "legs": "Legs", "quads": "Legs", "hamstrings": "Legs", "glutes": "Legs", "calves": "Legs",
            "triceps": "Triceps",
            "biceps": "Biceps"
        }

    def generate_volume_chart(self, weekly_plan):
        """Calculates total sets per muscle group and generates a bar chart."""
        volume_counts = {"Chest": 0, "Back": 0, "Legs": 0, "Shoulders": 0, "Triceps": 0, "Biceps": 0}

        # Calculate total sets
        for day, exercises in weekly_plan.items():
            if isinstance(exercises, str):  # Skip rest days
                continue

            for ex in exercises:
                # Extract number of sets from volume (e.g., "3x10-12" -> 3)
                try:
                    sets = int(ex['volume'].split('x')[0])
                except:
                    sets = 0

                target = str(ex.get('target', '')).lower()
                mapped_group = self.group_mapping.get(target, "Other")

                if mapped_group in volume_counts:
                    volume_counts[mapped_group] += sets

        # Generate Matplotlib Chart
        plt.figure(figsize=(8, 5))
        groups = list(volume_counts.keys())
        sets_data = list(volume_counts.values())

        # Create a neon-green bar chart to match our UI
        bars = plt.bar(groups, sets_data, color="#00e676", edgecolor="#121212")

        plt.title("Weekly Training Volume (Sets per Muscle Group)", color="white", fontsize=14)
        plt.xlabel("Muscle Groups", color="white")
        plt.ylabel("Total Sets", color="white")
        plt.xticks(color="white")
        plt.yticks(color="white")

        # Make background transparent/dark to match UI
        plt.gcf().set_facecolor('#1e1e1e')
        plt.gca().set_facecolor('#2c2c2c')

        # Add value labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, int(yval), ha='center', color='white',
                     fontweight='bold')

        # Save the plot to a BytesIO object and encode as base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", facecolor=plt.gcf().get_facecolor())
        plt.close()

        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"
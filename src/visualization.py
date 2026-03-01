import matplotlib.pyplot as plt
import io
import base64


class WorkoutVisualizer:
    def __init__(self):
        pass

    def generate_volume_chart(self, weekly_plan):
        volume_counts = {"Chest": 0, "Back": 0, "Legs": 0, "Shoulders": 0, "Triceps": 0, "Biceps": 0}
        type_counts = {"Compound": 0, "Isolation": 0}
        daily_sets = {}
        day_labels = []

        for day, exercises in weekly_plan.items():
            short_day = day.split(" - ")[0]

            if isinstance(exercises, str):
                daily_sets[short_day] = 0
                day_labels.append(short_day)
                continue

            day_total = 0
            for ex in exercises:
                try:
                    sets = int(ex['volume'].split('x')[0])
                except:
                    sets = 0

                day_total += sets

                mapped_group = ex.get('muscle_group', 'Other')
                if mapped_group in volume_counts:
                    volume_counts[mapped_group] += sets

                ex_type = ex.get('type', 'Other')
                if ex_type == "Compound" or ex_type == "Isolation":
                    type_counts[ex_type] += 1

            daily_sets[short_day] = day_total
            day_labels.append(short_day)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 16))
        fig.patch.set_facecolor('#1e1e1e')

        neon_green = "#00e676"
        dark_grey = "#2c2c2c"
        text_color = "white"

        # CHART 1: Bar Chart
        groups = list(volume_counts.keys())
        sets_data = list(volume_counts.values())

        bars = ax1.bar(groups, sets_data, color=neon_green, edgecolor="#121212")
        ax1.set_title("Sets per Muscle Group", color=text_color, fontsize=16, fontweight='bold', pad=15)
        ax1.set_ylabel("Total Sets", color=text_color, fontsize=12)
        ax1.tick_params(colors=text_color, labelsize=11)
        ax1.set_facecolor(dark_grey)

        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, yval + 0.3, int(yval), ha='center', color=text_color,
                     fontweight='bold', fontsize=12)

        # CHART 2: Pie Chart
        labels = list(type_counts.keys())
        sizes = list(type_counts.values())

        if sum(sizes) > 0:
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                    colors=[neon_green, "#555555"], textprops={'color': text_color, 'weight': 'bold', 'fontsize': 13},
                    wedgeprops={'edgecolor': '#1e1e1e', 'linewidth': 2})
            ax2.set_title("Exercise Type Ratio", color=text_color, fontsize=16, fontweight='bold', pad=15)
        else:
            ax2.text(0.5, 0.5, "No Data", ha='center', color=text_color, fontsize=14)
            ax2.axis('off')

        # CHART 3: Line Chart
        x_days = list(daily_sets.keys())
        y_sets = list(daily_sets.values())

        ax3.plot(x_days, y_sets, color=neon_green, marker='o', linewidth=3, markersize=10)
        ax3.fill_between(x_days, y_sets, color=neon_green, alpha=0.1)
        ax3.set_title("Daily Training Load", color=text_color, fontsize=16, fontweight='bold', pad=15)
        ax3.set_ylabel("Total Sets", color=text_color, fontsize=12)
        ax3.tick_params(colors=text_color, labelsize=11)
        ax3.set_facecolor(dark_grey)
        ax3.grid(color='#444444', linestyle='--', linewidth=0.5, alpha=0.7)

        plt.tight_layout(pad=4.0)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()

        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"
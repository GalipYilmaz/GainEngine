from fpdf import FPDF
import os


class PDFExporter:
    def generate_pdf(self, weekly_plan, filename="GainEngine_Workout_Plan.pdf"):
        """Generates a structured PDF file from the weekly workout plan."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(200, 15, txt="GainEngine - Your Smart Workout Plan", ln=True, align='C')
        pdf.ln(10)

        for day, exercises in weekly_plan.items():
            # Day Header
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 150, 0)  # Greenish color
            pdf.cell(200, 10, txt=day, ln=True)
            pdf.set_text_color(0, 0, 0)  # Reset to black

            if isinstance(exercises, str):
                pdf.set_font("Arial", 'I', 12)
                pdf.cell(200, 10, txt=f"  {exercises}", ln=True)
            else:
                pdf.set_font("Arial", 'B', 10)
                # Table Header
                pdf.cell(70, 8, "Exercise", border=1)
                pdf.cell(40, 8, "Target", border=1)
                pdf.cell(30, 8, "Sets/Reps", border=1)
                pdf.cell(50, 8, "Equipment", border=1)
                pdf.ln()

                pdf.set_font("Arial", '', 10)
                for ex in exercises:
                    pdf.cell(70, 8, str(ex['name'])[:35], border=1)
                    pdf.cell(40, 8, str(ex['target'])[:20], border=1)
                    pdf.cell(30, 8, str(ex['volume']), border=1)
                    pdf.cell(50, 8, str(ex['equipment'])[:25], border=1)
                    pdf.ln()
            pdf.ln(5)

        file_path = os.path.join("static", filename)
        pdf.output(file_path)
        return file_path
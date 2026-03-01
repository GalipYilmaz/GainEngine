# GainEngine

GainEngine is a full-stack, AI-powered workout plan generator and analyzer.

## Features

* **Smart Workout Generation:** Automatically creates perfectly balanced weekly routines (e.g., PPL, Upper/Lower, Full Body, Bro Split) tailored to specific equipment profiles (Bodyweight, Home Gym, Full Commercial Gym).
* **Scientific Volume Control:** Implements strict logic differentiating Major vs. Minor muscle groups. It prevents overtraining by capping weekly set volumes and adjusting sets based on muscle size (e.g., higher volume for Chest/Back, lower for Biceps).
* **Volume Compensation Algorithm:** If limited equipment restricts the number of available exercises for a specific muscle group, the engine intelligently multiplies the sets of available exercises to ensure weekly hypertrophy targets are still met.
* **AI-Powered Exercise Swap:** Utilizes a pre-trained K-Nearest Neighbors (KNN) similarity model to find the closest biomechanical alternative instantly if a user lacks the equipment or prefers a different movement.
* **Advanced Data Visualization:** Generates on-the-fly analytical dashboards using Matplotlib. It includes Bar Charts (muscle group volume), Pie Charts (compound vs. isolation ratio), and Line Charts (daily training load).
* **PDF Export:** Allows users to download their fully tailored weekly program as a neatly formatted PDF file.
* **RESTful API Architecture:** Built with FastAPI, ensuring fast, asynchronous request handling between the frontend and the machine learning engine.

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates
* **Data Science & AI:** Pandas, Scikit-Learn (KNN), Matplotlib

## Installation & Setup

Follow these instructions to get the project running on your local machine.

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/GainEngine.git](https://github.com/yourusername/GainEngine.git)
cd GainEngine
```

**2. Create a Virtual Environment**
*For Linux/macOS:*
```bash
python3 -m venv venv
source venv/bin/activate
```
*For Windows:*
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies**
Ensure your virtual environments is activated, then install the required packages:
```bash
pip install -r requirements.txt
```

**4. Run the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn src.api:app --reload
```

**5. Access the Application
Open your web browser and navigate to: http://127.0.0.1:8000


Developed by Galip Yılmaz

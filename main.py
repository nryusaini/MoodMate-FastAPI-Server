from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import random # Used for random placeholder scores

# --- 1. Define the Data Model for Incoming Data (Request Body) ---
# This class ensures the incoming JSON data from the Android app 
# matches the structure of your MoodEntry.java class.

class MoodEntry(BaseModel):
    # Field names MUST match the Java class MoodEntry.java
    mood_score: int
    hours_sleep: float
    social_tag: str
    activity_type: str

# --- 2. Initialize the FastAPI Application ---
app = FastAPI()

# --- 3. Define the POST Endpoint for Analysis ---
# This endpoint URL MUST match the one defined in your MoodMateApiService.java
@app.post("/api/v1/analyze_mood")
def calculate_mood_correlation(entry: MoodEntry):
    # -------------------------------------------------------------
    # PHASE 1: Data Preparation
    # -------------------------------------------------------------
    
    # In a real scenario, you would fetch *historical* data for the user
    # from Firebase to calculate a meaningful correlation. 
    # For now, we use a simple sample dataset combined with the incoming data.
    
    # Create sample historical data (Replace this with real Firebase data later)
    data = {
        'mood_score': [entry.mood_score, 4, 3, 5, 2, 4, 1, 5],
        'hours_sleep': [entry.hours_sleep, 7.5, 6.0, 8.0, 5.5, 7.0, 4.0, 8.5],
        'is_exercise': [1, 1, 0, 1, 0, 0, 0, 1],
        'is_social': [1 if entry.social_tag == "Friends" else 0, 1, 0, 1, 0, 1, 0, 1]
    }
    
    df = pd.DataFrame(data)

    # -------------------------------------------------------------
    # PHASE 2: Correlation Analysis (The Core Logic)
    # -------------------------------------------------------------
    
    # Calculate the correlation between mood score and sleep hours
    # .iloc[0, 1] retrieves the actual correlation value from the resulting matrix
    sleep_correlation = df[['mood_score', 'hours_sleep']].corr().iloc[0, 1]
    
    # Determine the personalized insight based on the calculated correlation
    if sleep_correlation > 0.5:
        insight_text = f"Great news! Your analysis shows a strong positive link (r={sleep_correlation:.2f}) between your mood and sleep. Maintain your current sleep habits!"
    elif sleep_correlation < -0.3:
        insight_text = f"Warning: Your analysis shows a negative link (r={sleep_correlation:.2f}) between your mood and sleep. You might feel happier when you get less sleep, which needs further review."
    else:
        insight_text = f"Your mood and sleep hours have a weak correlation (r={sleep_correlation:.2f}) this week. Try to be more consistent with your sleep schedule."

    # -------------------------------------------------------------
    # PHASE 3: Return Structured Response
    # -------------------------------------------------------------
    
    # The keys must match the @SerializedName in your MoodAnalysisResult.java class!
    return {
        "insight_text": insight_text,
        "correlation_score": float(sleep_correlation) # Ensure it's a standard float
    }

# --- Simple GET Endpoint (Used for initial testing only) ---
@app.get("/")
def read_root():
    return {"Hello": "MoodMate API is running and ready for POST requests."}
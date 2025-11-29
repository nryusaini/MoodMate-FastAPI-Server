from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import random 

# -----------------------------------------------------------------------------------------
# 1. DEFINE DATA MODELS (MUST match Java models)
# -----------------------------------------------------------------------------------------

class MoodEntry(BaseModel):
    # Core fields from Logmood
    mood_score: int
    hours_sleep: float
    social_tag: str
    activity_type: str
    
    # NEW FIELDS: Psychological Assessment Scores
    # These are Optional for now, but will be populated when you implement the quizzes.
    shs_score: Optional[float] = None     # Subjective Happiness Scale (Daily)
    panas_score: Optional[float] = None   # PANAS-SF (Weekly)
    ohq_score: Optional[float] = None     # Oxford Happiness Questionnaire (Monthly)

# The Incoming Request Body - A list of MoodEntry objects (the last 7 days of logs)
class MoodHistory(BaseModel):
    history: List[MoodEntry] 

# -----------------------------------------------------------------------------------------
# 2. INITIALIZE APPLICATION
# -----------------------------------------------------------------------------------------

app = FastAPI(title="MoodMate Analysis API")

# -----------------------------------------------------------------------------------------
# 3. ANALYSIS ENDPOINT (The Core Logic)
# -----------------------------------------------------------------------------------------

@app.post("/api/v1/analyze_mood")
def calculate_mood_correlation(history_data: MoodHistory):
    
    entries = history_data.history
    
    # Check if we have enough data (need at least 2 points for meaningful correlation)
    if len(entries) < 2:
        return {
            "insight_text": f"Log {2 - len(entries)} more entry(s) to start correlation analysis.",
            "correlation_score": 0.0
        }

    # 1. Data Preparation for Pandas (Using ONLY the real history data)
    # Extract lists of scores and sleep hours from the incoming history list
    mood_scores = [entry.mood_score for entry in entries]
    sleep_hours = [entry.hours_sleep for entry in entries]
    
    # Create DataFrame
    df = pd.DataFrame({
        'mood_score': mood_scores,
        'hours_sleep': sleep_hours
    })

    # 2. Correlation Analysis
    try:
        # Calculate the correlation between mood score and sleep hours
        sleep_correlation = df['mood_score'].corr(df['hours_sleep'])
    except Exception:
        # Handle case where correlation fails (e.g., all values are the same)
        sleep_correlation = 0.0
    
    # 3. Determine Personalized Insight based on the LATEST data
    # Calculate the average mood and sleep for better context
    avg_mood = df['mood_score'].mean()
    
    # Determine Insight Text
    if sleep_correlation > 0.4: 
        insight_text = f"Great news! Strong positive link (r={sleep_correlation:.2f}) between your mood and sleep. Maintain your current sleep habits!"
    elif sleep_correlation < -0.4:
        insight_text = f"Warning: Negative link (r={sleep_correlation:.2f}) between your mood and sleep. You may feel happier on less sleep. Review your schedule!"
    else:
        insight_text = f"Mood and sleep have a weak correlation (r={sleep_correlation:.2f}). Consistency is key for clearer patterns."
        
    # Add context based on the latest logged mood score (to confirm inputs are seen)
    latest_mood = entries[-1].mood_score
    if latest_mood <= 2:
        insight_text = f"Your latest mood was low (Score {latest_mood}). " + insight_text
    elif latest_mood == 5:
        insight_text = f"You are feeling joyful! " + insight_text


    # 4. Return Structured Response
    return {
        "insight_text": insight_text,
        "correlation_score": float(sleep_correlation)
    }

# --- Simple GET Endpoint (Used for initial testing only) ---
@app.get("/")
def read_root():
    return {"Hello": "MoodMate API is running and ready for POST requests."}

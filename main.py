from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np

# This model matches the MoodEntry class in your Android app
class MoodEntry(BaseModel):
    mood_score: int          # Emoji 1-5
    shs_score: Optional[float] = None     # Daily Assessment (1.0 - 7.0)
    panas_pa: Optional[int] = None        # Weekly Positive Affect (5 - 25)
    panas_na: Optional[int] = None        # Weekly Negative Affect (5 - 25)
    ohq_score: Optional[float] = None     # Monthly Assessment (1.0 - 6.0)
    timestamp: Optional[str] = None

class MoodHistory(BaseModel):
    history: List[MoodEntry]

app = FastAPI(title="MoodMate Psychometric Engine")

@app.get("/")
def read_root():
    return {"status": "MoodMate Analysis Server is Online", "engine": "v2.0-Psychometrics"}

@app.post("/api/v1/analyze_mood")
def analyze_mood_psychometrics(history_data: MoodHistory):
    entries = history_data.history
    
    if len(entries) < 1:
        return {
            "insight_text": "Welcome to MoodMate! Start logging your mood and complete assessments to unlock scientific insights.",
            "status": "Incomplete Data"
        }

    # Convert history to DataFrame for statistical analysis
    df = pd.DataFrame([e.dict() for e in entries])
    
    latest = entries[-1]
    insights = []

    # 1. MOOD STABILITY ANALYSIS (Using standard deviation of emoji logs)
    if len(df) > 2:
        mood_std = df['mood_score'].std()
        if mood_std < 0.8:
            insights.append("Your emotional state has been remarkably stable lately.")
        elif mood_std > 1.5:
            insights.append("You've been experiencing significant emotional shifts recently.")

    # 2. DAILY CROSS-VALIDATION (Emoji vs. Subjective Happiness Scale)
    if latest.shs_score is not None:
        # Normalize both to a 0.0 - 1.0 scale for comparison
        emoji_norm = (latest.mood_score - 1) / 4
        shs_norm = (latest.shs_score - 1) / 6
        
        diff = abs(emoji_norm - shs_norm)
        if diff < 0.15:
            insights.append("Your daily assessment strongly validates your current mood log.")
        else:
            insights.append("Your detailed assessment suggests your feelings are more complex than your quick log indicates.")

    # 3. WEEKLY AFFECT BALANCE (Positive vs. Negative Affect)
    if latest.panas_pa is not None and latest.panas_na is not None:
        if latest.panas_pa > (latest.panas_na + 5):
            insights.append("Scientifically, your positive emotions are dominating your week.")
        elif latest.panas_na > (latest.panas_pa):
            insights.append("Your emotional load is heavy this week; remember to practice self-care.")
        else:
            insights.append("You are maintaining a balanced emotional state this week.")

    # 4. MONTHLY HAPPINESS CHECK (Oxford Happiness Questionnaire)
    if latest.ohq_score is not None:
        if latest.ohq_score > 4.5:
            insights.append("Your monthly OHQ score indicates a high level of overall life satisfaction.")
        elif latest.ohq_score < 2.5:
            insights.append("Your monthly reflections suggest you may be going through a tough period.")

    # Combine all insights or provide a fallback
    if not insights:
        full_insight = "Continue completing your Daily, Weekly, and Monthly assessments to see a detailed psychological breakdown."
    else:
        full_insight = " ".join(insights)

    return {
        "insight_text": full_insight,
        "latest_score_summary": {
            "emoji": latest.mood_score,
            "shs": latest.shs_score,
            "ohq": latest.ohq_score
        },
        "server_status": "Analysis Complete"
    }

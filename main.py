from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np

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
            "insight_text": "Welcome to MoodMate! Start logging to unlock insights.",
            "chart_story": "Your chart will appear here once you start logging.",
            "status": "Incomplete Data"
        }

    df = pd.DataFrame([e.dict() for e in entries])
    latest = entries[-1]
    insights = []
    chart_story = "Your chart shows your emotional trends over time."

    # 1. MOOD STABILITY ANALYSIS
    if len(df) > 2:
        mood_std = df['mood_score'].std()
        if mood_std < 0.8:
            insights.append("Your emotional state has been remarkably stable lately.")
        elif mood_std > 1.5:
            insights.append("You've been experiencing significant emotional shifts recently.")

    # 2. DAILY CROSS-VALIDATION & CHART STORY LOGIC
    if latest.shs_score is not None:
        emoji_norm = (latest.mood_score - 1) / 4
        shs_norm = (latest.shs_score - 1) / 6
        diff = abs(emoji_norm - shs_norm)
        
        if diff < 0.15:
            insights.append("Your daily assessment strongly validates your current mood log.")
            chart_story = "The chart shows perfect alignment between your logs and assessments. You're very in tune with your feelings."
        elif shs_norm > emoji_norm:
            insights.append("Your detailed assessment suggests you are feeling better than your quick log indicates.")
            chart_story = "The green line (science) is higher than the blue area. You might be doing better than you realize!"
        else:
            insights.append("Your assessment suggests your feelings are more complex than your quick log shows.")
            chart_story = "The blue area (logs) is higher than the green line. You might be putting on a 'brave face' today."

    # 3. WEEKLY AFFECT BALANCE
    if latest.panas_pa is not None and latest.panas_na is not None:
        if latest.panas_pa > (latest.panas_na + 5):
            insights.append("Scientifically, your positive emotions are dominating your week.")
        elif latest.panas_na > (latest.panas_pa):
            insights.append("Your emotional load is heavy this week; remember self-care.")

    full_insight = " ".join(insights) if insights else "Continue assessments for a deeper breakdown."

    return {
        "insight_text": full_insight,
        "chart_story": chart_story,
        "server_status": "Analysis Complete"
    }

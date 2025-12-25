from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

class MoodEntry(BaseModel):
    mood_score: int # Emoji 1-5
    hours_sleep: float
    social_tag: str
    activity_type: str
    
    # Updated to handle PA and NA separately for Weekly
    shs_score: Optional[float] = None     # Daily (1.0 - 7.0)
    panas_pa: Optional[int] = None        # Weekly Positive (5 - 25)
    panas_na: Optional[int] = None        # Weekly Negative (5 - 25)
    ohq_score: Optional[float] = None     # Monthly (1.0 - 6.0)

class MoodHistory(BaseModel):
    history: List[MoodEntry] 

app = FastAPI(title="MoodMate Analysis API")

@app.post("/api/v1/analyze_mood")
def calculate_mood_correlation(history_data: MoodHistory):
    entries = history_data.history
    
    if len(entries) < 1:
        return {"insight_text": "Start logging to see your analysis!", "correlation_score": 0.0}

    # Convert to DataFrame for analysis
    df = pd.DataFrame([e.dict() for e in entries])

    # 1. Basic Sleep Correlation (Existing Logic)
    sleep_corr = df['mood_score'].corr(df['hours_sleep']) if len(df) > 1 else 0.0

    # 2. NEW: Scientific Validation Check
    # We compare the Emoji Mood (1-5) with SHS (1-7)
    latest = entries[-1]
    validation_text = ""
    
    if latest.shs_score is not None:
        # Normalize scores to 100% for comparison
        emoji_pct = (latest.mood_score / 5) * 100
        shs_pct = (latest.shs_score / 7) * 100
        
        if abs(emoji_pct - shs_pct) < 15:
            validation_text = "Your daily log strongly aligns with your happiness assessment. "
        else:
            validation_text = "Your quick log differs from your assessment; you might be feeling complex emotions today. "

    # 3. NEW: Weekly Affect Analysis
    weekly_text = ""
    if latest.panas_pa is not None and latest.panas_na is not None:
        if latest.panas_pa > latest.panas_na:
            weekly_text = "Your positive emotions are leading this week! "
        else:
            weekly_text = "You've had a heavy emotional load this week. "

    # 4. Final Insight Construction
    base_insight = f"Sleep correlation: {sleep_corr:.2f}. "
    if sleep_corr > 0.5:
        base_insight += "Quality sleep is clearly boosting your mood."
    
    full_insight = validation_text + weekly_text + base_insight

    return {
        "insight_text": full_insight.strip(),
        "correlation_score": float(sleep_corr),
        "latest_shs": latest.shs_score,
        "weekly_status": "Positive" if latest.panas_pa and latest.panas_pa > latest.panas_na else "Mixed"
    }

@app.get("/")
def read_root():
    return {"status": "MoodMate API is connected to Render and ready."}

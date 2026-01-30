@app.post("/api/v1/analyze_mood")
def analyze_psychometrics(history_data: MoodHistory):
    entries = history_data.history
    if len(entries) < 2:
        return {"insight_text": "Complete more assessments to unlock AI insights!"}

    df = pd.DataFrame([e.dict() for e in entries])
    
    # 1. MOOD STABILITY: Check if emoji scores are swinging wildly
    mood_std = df['mood_score'].std()
    stability_text = "Your mood has been very stable lately." if mood_std < 1.0 else "You've experienced some high emotional waves recently."

    # 2. CROSS-VALIDATION: Comparing Emoji (1-5) to SHS (1-7)
    # This proves the 'Daily Assessment' is working
    latest = entries[-1]
    validation_text = ""
    if latest.shs_score is not None:
        emoji_norm = (latest.mood_score / 5)
        shs_norm = (latest.shs_score / 7)
        diff = abs(emoji_norm - shs_norm)
        
        if diff < 0.15:
            validation_text = "Your daily assessment confirms your mood is genuine. "
        else:
            validation_text = "Your assessment suggests your feelings are deeper than your quick log shows. "

    # 3. WEEKLY TREND: Positive vs Negative Affect
    trend_text = ""
    if latest.panas_pa and latest.panas_na:
        if latest.panas_pa > latest.panas_na:
            trend_text = "Scientifically, your positive affect is dominating this week!"
        else:
            trend_text = "Your negative affect scores are higher; consider some self-care today."

    return {
        "insight_text": f"{validation_text} {stability_text} {trend_text}".strip(),
        "status": "Calculated via MoodMate Engine"
    }

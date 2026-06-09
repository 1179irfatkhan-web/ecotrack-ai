def get_ai_advice(data):

    score = 100

    if data["electricity_units"] > 100:
        score -= 20

    if data["transport_km"] > 50:
        score -= 20

    if data["meat_meals"] > 7:
        score -= 20

    if data["waste_kg"] > 10:
        score -= 20

    return f"""
Carbon Analysis

Total Carbon Footprint:
{data['total_carbon']} kg CO₂

Sustainability Score:
{score}/100

Recommendations:

• Reduce electricity consumption
• Use public transportation
• Reduce meat intake
• Recycle household waste
• Switch to energy efficient appliances
"""
import os
import google.generativeai as genai

def get_ai_advice(data):
    # Calculate rule-based sustainability score
    score = 100
    if data.get("electricity_units", 0) > 100:
        score -= 20
    if data.get("transport_km", 0) > 50:
        score -= 20
    if data.get("meat_meals", 0) > 7:
        score -= 20
    if data.get("waste_kg", 0) > 10:
        score -= 20

    rule_based_advice = f"""Carbon Analysis

Total Carbon Footprint:
{data.get('total_carbon', 0.0)} kg CO₂

Sustainability Score:
{score}/100

Recommendations:
• Reduce electricity consumption by turning off appliances
• Walk, bike, or take public transit for short trips
• Adopt a plant-rich diet or reduce meat portion sizes
• Recycle systematically and start composting organic waste
• Invest in energy-efficient household electronics"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return rule_based_advice

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"Analyze this carbon footprint data for an individual and provide personalized, friendly, "
            f"and actionable advice to reduce their footprint.\n"
            f"Metrics:\n"
            f"- Transport: {data.get('transport_km')} km\n"
            f"- Electricity: {data.get('electricity_units')} units (kWh)\n"
            f"- Meat Meals: {data.get('meat_meals')} meals\n"
            f"- Waste: {data.get('waste_kg')} kg\n"
            f"- Calculated CO2 total: {data.get('total_carbon')} kg CO2\n"
            f"Provide a brief overview of their impact, a score review ({score}/100), "
            f"and 3-5 concrete bullet points on what they can improve."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"{rule_based_advice}\n\n(Note: Live AI Advice offline: {str(e)})"
def calculate_carbon(data):

    transport = data["transport_km"] * 0.21

    electricity = data["electricity_units"] * 0.82

    food = data["meat_meals"] * 3.3

    waste = data["waste_kg"] * 0.57

    total = transport + electricity + food + waste

    return round(total, 2)
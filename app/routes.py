from flask import Flask, request, jsonify
from datetime import datetime, date
# Assume you have database models and functions defined elsewhere

app = Flask(__name__)

# Example impact factors (you'd likely fetch this from a database)
impact_factors = {
    "Recycling": {"carbon_saved_per_kg": 0.5, "waste_reduced_per_kg": 1.0, "unit": "kg"},
    "Water Usage": {"water_conserved_per_liter": 1.0, "unit": "liter"},
    "Public Transport": {"carbon_saved_per_km": 0.2, "unit": "km"},
    # ... more action types
}

@app.route('/api/users/<int:user_id>/actions', methods=['POST'])
def record_action(user_id):
    data = request.get_json()
    action_type = data.get('action_type')
    quantity = data.get('quantity')
    unit = data.get('unit')
    date_recorded = datetime.now()

    if not all([action_type, quantity, unit]):
        return jsonify({"error": "Missing required fields"}), 400

    if action_type not in impact_factors or impact_factors[action_type]['unit'] != unit:
        return jsonify({"error": "Invalid action type or unit"}), 400

    # Save the action to the database (replace with your actual database logic)
    action_id = save_user_action(user_id, action_type, quantity, unit, date_recorded)

    # Calculate impact (replace with more robust logic)
    carbon_saved = 0
    water_conserved = 0
    waste_reduced = 0

    if action_type == "Recycling":
        carbon_saved = quantity * impact_factors[action_type]['carbon_saved_per_kg']
        waste_reduced = quantity * impact_factors[action_type]['waste_reduced_per_kg']
    elif action_type == "Water Usage":
        water_conserved = quantity * impact_factors[action_type]['water_conserved_per_liter']
    elif action_type == "Public Transport":
        carbon_saved = quantity * impact_factors[action_type]['carbon_saved_per_km']

    # Potentially update aggregate tables

    return jsonify({"message": "Action recorded successfully", "action_id": action_id}), 201

@app.route('/api/users/<int:user_id>/impact', methods=['GET'])
def get_user_impact(user_id):
    today = date.today()
    first_day_of_month = today.replace(day=1)

    # Fetch user's actions for the current month (replace with your database logic)
    monthly_actions = get_user_actions_by_date(user_id, first_day_of_month, today)

    total_carbon_saved = 0
    total_water_conserved = 0
    total_waste_reduced = 0

    for action in monthly_actions:
        factor = impact_factors.get(action['action_type'])
        if factor:
            if 'carbon_saved_per_unit' in factor:
                total_carbon_saved += action['quantity'] * factor['carbon_saved_per_unit']
            if 'water_conserved_per_unit' in factor:
                total_water_conserved += action['quantity'] * factor['water_conserved_per_unit']
            if 'waste_reduced_per_unit' in factor:
                total_waste_reduced += action['quantity'] * factor['waste_reduced_per_unit']

    # Fetch total actions completed this week (replace with your database logic)
    start_of_week = today - timedelta(days=today.weekday())
    weekly_actions_count = get_user_actions_count_by_date(user_id, start_of_week, today)

    # Calculate percentage change (you'll need to fetch previous period's data)
    previous_month = first_day_of_month.replace(month=first_day_of_month.month - 1)
    last_day_of_previous_month = (first_day_of_month - timedelta(days=1)).replace(day=1) - timedelta(days=1)
    previous_month_total_carbon = get_previous_month_carbon_saved(user_id, previous_month, last_day_of_previous_month)
    carbon_saved_percentage_change = calculate_percentage_change(previous_month_total_carbon, total_carbon_saved)

    # ... similar calculations for water, waste, and weekly actions

    return jsonify({
        "carbon_saved": f"{total_carbon_saved:.2f} kg",
        "carbon_saved_percentage_change": f"{carbon_saved_percentage_change:.0f}% this month",
        "water_conserved": f"{total_water_conserved:.2f} liters",
        "water_conserved_percentage_change": f"{water_conserved_percentage_change:.0f}% this month",
        "waste_reduced": f"{total_waste_reduced:.2f} kg",
        "waste_reduced_percentage_change": f"{waste_reduced_percentage_change:.0f}% this month",
        "actions_completed": weekly_actions_count,
        "actions_completed_percentage_change": "+X% this week" # You'll need to implement this calculation
    })

def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return 100 if new_value > 0 else 0
    return ((new_value - old_value) / old_value) * 100

# ... (Database interaction functions would go here)
from flask import Blueprint, jsonify
from app.supabase_client import get_users

@bp.route('/api/users', methods=['GET'])
def api_get_users():
    users = get_users()
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
import json
import random
import time
from datetime import datetime

# Configuration of data 
MOCK_DATA_FILE = "mock_data.json"
MERCHANTS = ["Amazon", "Apple", "Walmart", "Steam", "Shell", "Whole Foods"]
TRANSACTION_TYPES = ["E-COMMERCE", "BANK_TRANSFER", "POS_PURCHASE"]

def load_user_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_event(user_profile):
    user_id = user_profile['user_id']
    historic_data = user_profile.get('historic_data', {})
    avg_income = historic_data.get('avg_monthly_income', 5000)
    
    event_type = random.choice(TRANSACTION_TYPES)
    
    if event_type == "E-COMMERCE":
        amount = round(random.uniform(10.0, 500.0), 2)
        merchant = random.choice(MERCHANTS)
        description = f"Purchase at {merchant}"
    elif event_type == "BANK_TRANSFER":
        # Simulating a salary credit based on avg income deviation or a large transfer
        amount = round(random.uniform(avg_income * 0.1, avg_income * 0.5), 2)
        description = "Salary Credit / Monthly Deposit"
    else:
        # POS Purchase
        amount = round(random.uniform(5.0, 100.0), 2)
        description = "Point of Sale Transaction"

    return {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "event_source": "STREAMING_BUS",
        "data": {
            "type": event_type,
            "amount": amount,
            "currency": "USD",
            "description": description,
            "potential_interest_flag": amount > 1000 # Logic for the "Propensity Model"
        }
    }

def run_simulation(duration_seconds=10):
    print(f"--- Starting Event Stream Simulation ---")
    
    try:
        users = load_user_data(MOCK_DATA_FILE)
    except FileNotFoundError:
        print(f"Error: {MOCK_DATA_FILE} not found.")
        return

    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        user_profile = random.choice(users)
        event = generate_event(user_profile)
        
        # In stage 2, we would send this to a Kafka Producer or an API endpoint
        print(json.dumps(event, indent=2))
        
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    run_simulation(10)
"""
FlightSage Flight Database
Realistic flight data for our AI travel agent.
"""

import random
from datetime import datetime, timedelta

# ============================================================
# AIRPORT DATABASE
# ============================================================
AIRPORTS = {
    "JFK": {"city": "New York", "country": "USA", "name": "John F. Kennedy"},
    "LAX": {"city": "Los Angeles", "country": "USA", "name": "Los Angeles International"},
    "ORD": {"city": "Chicago", "country": "USA", "name": "O'Hare International"},
    "MIA": {"city": "Miami", "country": "USA", "name": "Miami International"},
    "SFO": {"city": "San Francisco", "country": "USA", "name": "San Francisco International"},
    "LHR": {"city": "London", "country": "UK", "name": "Heathrow"},
    "CDG": {"city": "Paris", "country": "France", "name": "Charles de Gaulle"},
    "NRT": {"city": "Tokyo", "country": "Japan", "name": "Narita International"},
    "DXB": {"city": "Dubai", "country": "UAE", "name": "Dubai International"},
    "SIN": {"city": "Singapore", "country": "Singapore", "name": "Changi"},
    "BKK": {"city": "Bangkok", "country": "Thailand", "name": "Suvarnabhumi"},
    "CUN": {"city": "Cancun", "country": "Mexico", "name": "Cancun International"},
    "BCN": {"city": "Barcelona", "country": "Spain", "name": "El Prat"},
    "FCO": {"city": "Rome", "country": "Italy", "name": "Fiumicino"},
    "DEL": {"city": "Delhi", "country": "India", "name": "Indira Gandhi International"},
    "BOM": {"city": "Mumbai", "country": "India", "name": "Chhatrapati Shivaji"},
    "SYD": {"city": "Sydney", "country": "Australia", "name": "Kingsford Smith"},
    "HKG": {"city": "Hong Kong", "country": "Hong Kong", "name": "Hong Kong International"},
    "ICN": {"city": "Seoul", "country": "South Korea", "name": "Incheon International"},
    "GRU": {"city": "Sao Paulo", "country": "Brazil", "name": "Guarulhos International"},
}

# ============================================================
# FLIGHT ROUTES WITH BASE PRICES
# (Realistic prices based on actual market rates)
# ============================================================
ROUTES = [
    # USA Domestic
    {"from": "JFK", "to": "LAX", "base_price": 320, "duration_hours": 6, "airlines": ["Delta", "JetBlue", "American"]},
    {"from": "JFK", "to": "ORD", "base_price": 180, "duration_hours": 3, "airlines": ["United", "American", "Delta"]},
    {"from": "JFK", "to": "MIA", "base_price": 220, "duration_hours": 3, "airlines": ["JetBlue", "American", "Delta"]},
    {"from": "JFK", "to": "SFO", "base_price": 350, "duration_hours": 6.5, "airlines": ["JetBlue", "United", "Delta"]},
    {"from": "LAX", "to": "ORD", "base_price": 280, "duration_hours": 4.5, "airlines": ["United", "American", "Spirit"]},
    
    # USA to Europe
    {"from": "JFK", "to": "LHR", "base_price": 650, "duration_hours": 7, "airlines": ["British Airways", "Virgin Atlantic", "Delta"]},
    {"from": "JFK", "to": "CDG", "base_price": 720, "duration_hours": 7.5, "airlines": ["Air France", "Delta", "American"]},
    {"from": "JFK", "to": "FCO", "base_price": 780, "duration_hours": 8.5, "airlines": ["ITA Airways", "Delta", "American"]},
    {"from": "JFK", "to": "BCN", "base_price": 690, "duration_hours": 8, "airlines": ["Iberia", "United", "Delta"]},
    {"from": "LAX", "to": "LHR", "base_price": 850, "duration_hours": 11, "airlines": ["British Airways", "American", "Virgin Atlantic"]},
    
    # USA to Asia
    {"from": "JFK", "to": "NRT", "base_price": 1100, "duration_hours": 14, "airlines": ["ANA", "Japan Airlines", "United"]},
    {"from": "LAX", "to": "NRT", "base_price": 950, "duration_hours": 11.5, "airlines": ["ANA", "Japan Airlines", "Delta"]},
    {"from": "SFO", "to": "ICN", "base_price": 1050, "duration_hours": 12, "airlines": ["Korean Air", "Asiana", "United"]},
    {"from": "LAX", "to": "HKG", "base_price": 1180, "duration_hours": 15, "airlines": ["Cathay Pacific", "United", "Singapore Airlines"]},
    {"from": "JFK", "to": "BKK", "base_price": 1250, "duration_hours": 18, "airlines": ["Thai Airways", "Emirates", "Qatar Airways"]},
    {"from": "JFK", "to": "SIN", "base_price": 1350, "duration_hours": 18.5, "airlines": ["Singapore Airlines", "United", "Emirates"]},
    
    # USA to Middle East
    {"from": "JFK", "to": "DXB", "base_price": 980, "duration_hours": 12.5, "airlines": ["Emirates", "Qatar Airways", "Etihad"]},
    {"from": "LAX", "to": "DXB", "base_price": 1100, "duration_hours": 16, "airlines": ["Emirates", "Qatar Airways"]},
    
    # USA to India
    {"from": "JFK", "to": "DEL", "base_price": 1050, "duration_hours": 15, "airlines": ["Air India", "Emirates", "United"]},
    {"from": "JFK", "to": "BOM", "base_price": 1080, "duration_hours": 16, "airlines": ["Air India", "Emirates", "Lufthansa"]},
    
    # USA to Mexico/Caribbean
    {"from": "JFK", "to": "CUN", "base_price": 380, "duration_hours": 4, "airlines": ["JetBlue", "Aeromexico", "Delta"]},
    {"from": "MIA", "to": "CUN", "base_price": 220, "duration_hours": 2, "airlines": ["American", "Aeromexico", "Spirit"]},
    {"from": "LAX", "to": "CUN", "base_price": 420, "duration_hours": 5, "airlines": ["Delta", "American", "Volaris"]},
    
    # USA to Australia
    {"from": "LAX", "to": "SYD", "base_price": 1450, "duration_hours": 15, "airlines": ["Qantas", "Delta", "United"]},
    {"from": "SFO", "to": "SYD", "base_price": 1380, "duration_hours": 14.5, "airlines": ["Qantas", "United", "Air New Zealand"]},
    
    # USA to South America
    {"from": "JFK", "to": "GRU", "base_price": 780, "duration_hours": 10, "airlines": ["LATAM", "American", "Delta"]},
    {"from": "MIA", "to": "GRU", "base_price": 580, "duration_hours": 8.5, "airlines": ["LATAM", "American", "Avianca"]},
    
    # Europe internal
    {"from": "LHR", "to": "CDG", "base_price": 180, "duration_hours": 1.5, "airlines": ["British Airways", "Air France", "EasyJet"]},
    {"from": "LHR", "to": "FCO", "base_price": 220, "duration_hours": 2.5, "airlines": ["British Airways", "Ryanair", "ITA Airways"]},
    {"from": "CDG", "to": "BCN", "base_price": 160, "duration_hours": 2, "airlines": ["Air France", "Iberia", "Vueling"]},
]


# ============================================================
# FLIGHT SEARCH FUNCTION
# ============================================================
def search_flights(origin: str, destination: str, departure_date: str = None, max_results: int = 5):
    """
    Search for flights between two airports.
    
    Args:
        origin: Airport code (e.g., 'JFK')
        destination: Airport code (e.g., 'LAX')
        departure_date: Date in 'YYYY-MM-DD' format (optional)
        max_results: Maximum number of results to return
    
    Returns:
        List of flight options with prices and details
    """
    
    # Find matching routes
    matching_routes = [r for r in ROUTES if r["from"] == origin.upper() and r["to"] == destination.upper()]
    
    if not matching_routes:
        return {
            "success": False,
            "message": f"No flights found from {origin} to {destination}. Try one of these airports: {list(AIRPORTS.keys())}"
        }
    
    route = matching_routes[0]
    flights = []
    
    # Generate flight options with realistic variations
    for i in range(min(max_results, len(route["airlines"]))):
        airline = route["airlines"][i]
        
        # Add realistic price variation (±15%)
        price_variation = random.uniform(0.85, 1.15)
        price = round(route["base_price"] * price_variation, 2)
        
        # Add duration variation (±30 min)
        duration = route["duration_hours"] + random.uniform(-0.5, 0.5)
        
        # Generate flight number
        flight_number = f"{airline[:2].upper()}{random.randint(100, 9999)}"
        
        flights.append({
            "flight_number": flight_number,
            "airline": airline,
            "from": origin.upper(),
            "from_city": AIRPORTS[origin.upper()]["city"],
            "to": destination.upper(),
            "to_city": AIRPORTS[destination.upper()]["city"],
            "price_usd": price,
            "duration_hours": round(duration, 1),
            "departure_date": departure_date or "Flexible",
            "stops": 0 if duration < 8 else random.choice([0, 1])
        })
    
    # Sort by price
    flights.sort(key=lambda x: x["price_usd"])
    
    return {
        "success": True,
        "origin": origin.upper(),
        "destination": destination.upper(),
        "results_count": len(flights),
        "flights": flights
    }


def get_available_destinations(origin: str = None):
    """Get list of all destinations we have flights to."""
    if origin:
        destinations = list(set(r["to"] for r in ROUTES if r["from"] == origin.upper()))
        return destinations
    return list(AIRPORTS.keys())


# ============================================================
# TEST IT!
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("✈️  FLIGHTSAGE FLIGHT DATABASE - TEST")
    print("=" * 60)
    
    # Test 1: Search NYC to Tokyo
    print("\n🔍 Test 1: Searching JFK → NRT (Tokyo)")
    print("-" * 60)
    results = search_flights("JFK", "NRT", "2026-06-15")
    
    if results["success"]:
        print(f"Found {results['results_count']} flights:\n")
        for flight in results["flights"]:
            print(f"  ✈️  {flight['airline']} - {flight['flight_number']}")
            print(f"      {flight['from_city']} → {flight['to_city']}")
            print(f"      💰 ${flight['price_usd']} | ⏱️  {flight['duration_hours']}h | Stops: {flight['stops']}")
            print()
    
    # Test 2: Search NYC to Cancun
    print("\n🔍 Test 2: Searching JFK → CUN (Cancun)")
    print("-" * 60)
    results = search_flights("JFK", "CUN", "2026-03-15")
    
    if results["success"]:
        print(f"Found {results['results_count']} flights:\n")
        for flight in results["flights"]:
            print(f"  ✈️  {flight['airline']} - ${flight['price_usd']}")
    
    # Test 3: Show available destinations from JFK
    print("\n🌍 Test 3: All destinations from JFK")
    print("-" * 60)
    destinations = get_available_destinations("JFK")
    for dest in destinations:
        print(f"  📍 {dest} - {AIRPORTS[dest]['city']}, {AIRPORTS[dest]['country']}")
    
    print("\n" + "=" * 60)
    print("✅ Flight database working perfectly!")
    print("=" * 60)
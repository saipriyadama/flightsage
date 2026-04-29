"""
FlightSage - Search Agent
The "hunter" that searches the flight database for matching flights.
"""

import sys
import os

# Add parent directory to path so we can import flight_database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flight_database import search_flights, AIRPORTS


class SearchAgent:
    """
    The Search Agent takes structured trip data from the Strategist
    and finds matching flights in the database.
    
    This is our 'MCP-style tool' — it gives Claude the ability
    to search real flight data.
    """
    
    def __init__(self):
        self.name = "Search Agent"
        self.role = "Flight Hunter"
    
    def search_for_destinations(self, destinations: list, origin: str = "JFK", 
                                 budget_max: float = 1500, max_per_destination: int = 3) -> dict:
        """
        Search flights to multiple destinations and filter by budget.
        
        Args:
            destinations: List of airport codes (e.g., ["CUN", "MIA"])
            origin: Departure airport code (default JFK)
            budget_max: Maximum price in USD
            max_per_destination: Max flights to return per destination
        
        Returns:
            Dictionary with search results organized by destination
        """
        all_results = {}
        valid_destinations = []
        invalid_destinations = []
        
        for destination in destinations:
            destination = destination.upper()
            
            # Skip if destination not in our database
            if destination not in AIRPORTS:
                invalid_destinations.append(destination)
                continue
            
            # Search the database
            search_result = search_flights(
                origin=origin,
                destination=destination,
                max_results=max_per_destination
            )
            
            if not search_result.get("success"):
                continue
            
            # Filter by budget
            affordable_flights = [
                f for f in search_result["flights"]
                if f["price_usd"] <= budget_max
            ]
            
            if affordable_flights:
                # Calculate stats
                cheapest = min(f["price_usd"] for f in affordable_flights)
                most_expensive = max(f["price_usd"] for f in affordable_flights)
                
                all_results[destination] = {
                    "destination_city": AIRPORTS[destination]["city"],
                    "destination_country": AIRPORTS[destination]["country"],
                    "flights_count": len(affordable_flights),
                    "cheapest_price": cheapest,
                    "most_expensive_price": most_expensive,
                    "flights": affordable_flights
                }
                valid_destinations.append(destination)
        
        return {
            "success": len(valid_destinations) > 0,
            "origin": origin,
            "budget_max": budget_max,
            "destinations_searched": len(destinations),
            "destinations_with_results": len(valid_destinations),
            "invalid_destinations": invalid_destinations,
            "results": all_results
        }
    
    def find_best_deal(self, search_results: dict) -> dict:
        """
        Find the absolute cheapest flight across all destinations.
        
        Args:
            search_results: Output from search_for_destinations()
        
        Returns:
            Best deal info
        """
        if not search_results.get("success"):
            return {"error": "No valid search results"}
        
        best_flight = None
        best_destination = None
        best_price = float('inf')
        
        for dest, data in search_results["results"].items():
            for flight in data["flights"]:
                if flight["price_usd"] < best_price:
                    best_price = flight["price_usd"]
                    best_flight = flight
                    best_destination = dest
        
        if best_flight:
            return {
                "success": True,
                "best_destination": best_destination,
                "destination_city": AIRPORTS[best_destination]["city"],
                "flight": best_flight,
                "savings_message": f"Best deal: ${best_price} to {AIRPORTS[best_destination]['city']}!"
            }
        
        return {"error": "No flights found"}


# ============================================================
# TEST IT!
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 SEARCH AGENT - TEST")
    print("=" * 60)
    
    agent = SearchAgent()
    
    # ============================================================
    # TEST 1: Warm destinations under $800
    # ============================================================
    print("\n📨 Test 1: Searching warm destinations from JFK under $800")
    print("-" * 60)
    
    results = agent.search_for_destinations(
        destinations=["CUN", "MIA", "BKK"],
        origin="JFK",
        budget_max=800
    )
    
    print(f"✅ Searched {results['destinations_searched']} destinations")
    print(f"✅ Found flights for {results['destinations_with_results']} destinations\n")
    
    for dest, data in results["results"].items():
        print(f"📍 {dest} - {data['destination_city']}, {data['destination_country']}")
        print(f"   💰 Cheapest: ${data['cheapest_price']}")
        print(f"   ✈️  Available flights: {data['flights_count']}")
        print(f"   Top option:")
        for flight in data["flights"][:1]:
            print(f"      {flight['airline']} - {flight['flight_number']}: ${flight['price_usd']} ({flight['duration_hours']}h)")
        print()
    
    # ============================================================
    # TEST 2: Find the BEST deal
    # ============================================================
    print("\n💎 Test 2: Finding the absolute best deal")
    print("-" * 60)
    
    best = agent.find_best_deal(results)
    
    if best.get("success"):
        flight = best["flight"]
        print(f"🏆 {best['savings_message']}")
        print(f"   Airline: {flight['airline']}")
        print(f"   Flight: {flight['flight_number']}")
        print(f"   Duration: {flight['duration_hours']}h")
        print(f"   Stops: {flight['stops']}")
    
    # ============================================================
    # TEST 3: European destinations under $700
    # ============================================================
    print("\n📨 Test 3: European destinations from JFK under $700")
    print("-" * 60)
    
    eu_results = agent.search_for_destinations(
        destinations=["LHR", "CDG", "FCO", "BCN"],
        origin="JFK",
        budget_max=700
    )
    
    if eu_results["destinations_with_results"] == 0:
        print(" No European destinations under $700 from JFK")
        print("   (European flights typically cost $650-800 from JFK)")
    else:
        for dest, data in eu_results["results"].items():
            print(f" {dest}: ${data['cheapest_price']}")
    
    # ============================================================
    # TEST 4: Invalid destination handling
    # ============================================================
    print("\n📨 Test 4: Handling invalid destinations")
    print("-" * 60)
    
    bad_results = agent.search_for_destinations(
        destinations=["XYZ", "ABC", "JFK"],  # JFK to JFK won't work
        origin="JFK",
        budget_max=2000
    )
    
    print(f"Invalid destinations skipped: {bad_results['invalid_destinations']}")
    
    print("\n" + "=" * 60)
    print(" Search Agent is working!")
    print("=" * 60)
"""
FlightSage - Strategist Agent (with Multi-Turn Memory!)
The "brain" that understands user requests across multiple turns.
"""

import os
import json
import re
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


class StrategistAgent:
    """
    The Strategist understands fuzzy user requests AND maintains conversation memory.
    
    NEW: Multi-turn conversation support
    - Remembers previous messages
    - Asks clarifying questions when info is missing
    - Refines understanding over multiple turns
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-7"
        
        self.system_prompt = """You are the Strategist Agent for FlightSage, an AI travel platform.

You have TWO MODES:

MODE 1 - INFO GATHERING (when user request is incomplete):
If the user's request is missing critical info (budget, dates, destinations), 
ask ONE friendly clarifying question. Be conversational.

Example:
User: "I want a beach trip"
You: "Great choice! What's your budget range, and when are you thinking of traveling?"

MODE 2 - STRUCTURED EXTRACTION (when you have enough info):
Once you have enough information, return a JSON object with these fields:
- destinations: List of suggested airport codes
- origin: Departure airport (default "JFK")
- budget_max: Maximum budget in USD
- travel_month: Preferred month
- duration_days: Trip length
- preferences: List of trip characteristics
- trip_type: leisure/business/adventure/romantic/family
- needs_more_info: true/false

DECISION RULES:
- If user mentions: budget OR destination → Enough info, extract
- If user just says "trip" or "vacation" with no details → Ask for budget
- If you've already asked once → Just extract with defaults

Available airports: JFK, LAX, ORD, MIA, SFO, LHR, CDG, NRT, DXB, SIN, BKK, CUN, BCN, FCO, DEL, BOM, SYD, HKG, ICN, GRU

CRITICAL OUTPUT RULES:
- For MODE 1: Just return your question as a friendly message (no JSON!)
- For MODE 2: Return ONLY a JSON object, nothing else
- Determine the mode based on whether you have enough info to plan
CRITICAL: Match destinations to user's TRIP TYPE:
- "Romantic" → Paris (CDG), Rome (FCO), Barcelona (BCN)
- "Beach" → Miami (MIA), Cancun (CUN)  
- "Adventure" → Bangkok (BKK), Delhi (DEL)
- "Cultural" → Tokyo (NRT), Rome (FCO)
Don't pick beaches for "romantic" requests!

Examples:

User: "Beach trip"
Response: "Sounds amazing! What's your budget and when would you like to go? 🏖️"

User: "Beach trip in March, $800 budget"  
Response: {"destinations": ["CUN", "MIA", "BKK"], "origin": "JFK", "budget_max": 800, "travel_month": "March", "duration_days": 7, "preferences": ["beach"], "trip_type": "leisure", "needs_more_info": false}
"""
    
    def understand_request(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Take a natural language request (with optional history) and return either:
        - A clarifying question (if info is missing)
        - Structured data (if enough info)
        
        Args:
            user_message: User's latest message
            conversation_history: List of previous messages [{role, content}, ...]
        
        Returns:
            Dictionary with response type and data
        """
        try:
            # Build the messages array with history
            messages = []
            
            if conversation_history:
                # Add previous turns
                messages.extend(conversation_history)
            
            # Add the current message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text.strip()
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                # MODE 2: Got structured data
                try:
                    structured_data = json.loads(json_match.group(0))
                    return {
                        "success": True,
                        "type": "extracted",  # We got structured data
                        "data": structured_data,
                        "message": "Got it! Searching now..."
                    }
                except json.JSONDecodeError:
                    pass
            
            # MODE 1: Got a clarifying question
            return {
                "success": True,
                "type": "question",  # We need more info
                "message": response_text,
                "data": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================
# TEST IT!
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 STRATEGIST AGENT - MULTI-TURN TEST")
    print("=" * 60)
    
    agent = StrategistAgent()
    
    # Test 1: Vague request (should ask for clarification)
    print("\n📨 Test 1: Vague request")
    print("-" * 60)
    print("User: 'I want a vacation'")
    
    result = agent.understand_request("I want a vacation")
    print(f"Type: {result['type']}")
    print(f"AI: {result['message']}")
    
    # Test 2: With history (now provides budget)
    print("\n📨 Test 2: Follow-up with budget")
    print("-" * 60)
    
    history = [
        {"role": "user", "content": "I want a vacation"},
        {"role": "assistant", "content": "Sounds great! What's your budget and where would you like to go?"}
    ]
    
    result = agent.understand_request("Beach trip in March, around $800", history)
    print(f"Type: {result['type']}")
    if result['type'] == 'extracted':
        print(f"Got structured data: {result['data']}")
    else:
        print(f"AI: {result['message']}")
    
    # Test 3: Complete request (no clarification needed)
    print("\n📨 Test 3: Complete request")
    print("-" * 60)
    print("User: 'Cherry blossoms in Japan, budget $1500'")
    
    result = agent.understand_request("Cherry blossoms in Japan, budget $1500")
    print(f"Type: {result['type']}")
    if result['type'] == 'extracted':
        print(f"✅ Got structured data immediately!")
        print(f"Data: {result['data']}")
    
    print("\n" + "=" * 60)
    print("✅ Multi-turn Strategist working!")
    print("=" * 60)
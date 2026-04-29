"""
FlightSage - Orchestrator with Error Handling
Coordinates all 4 agents with proper error handling for edge cases.
"""

import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.strategist_agent import StrategistAgent
from agents.search_agent import SearchAgent
from agents.knowledge_agent import KnowledgeAgent

load_dotenv()


class FlightSageOrchestrator:
    """
    Main orchestrator that coordinates all agents.
    
    Flow:
    1. Strategist understands request
    2. Search finds flights
    3. Knowledge retrieves tips
    4. Claude synthesizes recommendation
    
    Handles errors gracefully at each step.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-7"
        
        print("🚀 Initializing FlightSage agents...")
        self.strategist = StrategistAgent()
        self.search_agent = SearchAgent()
        self.knowledge_agent = KnowledgeAgent()
        print("✅ All agents ready!\n")
        
        # Conversation history for multi-turn
        self.conversation_history = []
    
    def reset_conversation(self):
        """Start a new conversation."""
        self.conversation_history = []
    
    def chat(self, user_message: str) -> dict:
        """
        Process a user message through all agents.
        
        Returns:
        - trip_plan: Complete trip with flights, tips, dashboard data
        - question: AI needs more info
        - no_results: No flights found in budget
        - error: Something went wrong
        """
        
        print(f"📨 Processing: \"{user_message}\"\n")
        
        # ============================================================
        # STEP 1: STRATEGIST - Understand request
        # ============================================================
        print("🧠 [Strategist] Analyzing your message...")
        strategist_result = self.strategist.understand_request(
            user_message=user_message,
            conversation_history=self.conversation_history
        )
        
        if not strategist_result["success"]:
            error_msg = "Sorry, I couldn't understand your request. Can you try rephrasing?"
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            print(f"   ❌ Failed to understand\n")
            return {
                "success": False,
                "type": "error",
                "message": error_msg
            }
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # ============================================================
        # CASE 1: Strategist asks clarifying question
        # ============================================================
        if strategist_result["type"] == "question":
            ai_message = strategist_result["message"]
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            print(f"   💬 Asking for clarification\n")
            return {
                "success": True,
                "type": "question",
                "message": ai_message,
                "conversation_history": self.conversation_history
            }
        
        # ============================================================
        # CASE 2: Got enough info, plan the trip
        # ============================================================
        trip_data = strategist_result["data"]
        print(f"   ✅ Understood: {trip_data.get('destinations', [])}\n")
        
        # ============================================================
        # STEP 2: SEARCH - Find flights
        # ============================================================
        print("🔍 [Search Agent] Hunting for flights...")
        search_results = self.search_agent.search_for_destinations(
            destinations=trip_data.get("destinations", []),
            origin=trip_data.get("origin", "JFK"),
            budget_max=trip_data.get("budget_max", 1500)
        )
        
        # ⭐ KEY FIX: Handle "no flights found" gracefully
        if not search_results["success"]:
            error_msg = f"❌ No flights found within ${trip_data.get('budget_max')} budget. Try a higher budget or different destination?"
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            print(f"   ❌ No flights found\n")
            return {
                "success": False,
                "type": "no_results",
                "message": error_msg
            }
        
        print(f"   ✅ Found flights for {search_results['destinations_with_results']} destinations\n")
        
        # ============================================================
        # STEP 3: SEARCH - Get best deal
        # ============================================================
        print("💎 [Search Agent] Finding the best deal...")
        best_deal = self.search_agent.find_best_deal(search_results)
        print(f"   ✅ Best deal: {best_deal['destination_city']} ${best_deal['flight']['price_usd']}\n")
        
        # ============================================================
        # STEP 4: KNOWLEDGE - Get insider tips
        # ============================================================
        print("📚 [Knowledge Agent] Retrieving insider tips...")
        knowledge_results = self.knowledge_agent.search(
            query=user_message,
            n_results=3,
            min_relevance=0.40
        )
        
        # Get destination-specific tips
        if best_deal.get("success"):
            destination_tips = self.knowledge_agent.get_destination_tips(
                destination=best_deal["destination_city"],
                n_results=2,
                min_relevance=0.40
            )
        else:
            destination_tips = {"tips": []}
        
        # Combine and deduplicate tips
        all_tips = []
        if knowledge_results.get("success"):
            all_tips.extend(knowledge_results["tips"])
        if destination_tips.get("success"):
            all_tips.extend(destination_tips["tips"])
        
        seen_tips = set()
        unique_tips = []
        for tip in all_tips:
            if tip["tip"] not in seen_tips:
                seen_tips.add(tip["tip"])
                unique_tips.append(tip)
        
        print(f"   ✅ Found {len(unique_tips)} relevant tips\n")
        
        # ============================================================
        # STEP 5: SYNTHESIS - Generate recommendation
        # ============================================================
        print("✨ [Orchestrator] Generating personalized recommendation...")
        summary = self._generate_summary(
            user_request=user_message,
            trip_data=trip_data,
            search_results=search_results,
            best_deal=best_deal,
            tips=unique_tips
        )
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": summary
        })
        
        print("   ✅ Done!\n")
        
        return {
            "success": True,
            "type": "trip_plan",
            "message": summary,
            "summary": summary,
            "understood_as": trip_data,
            "search_results": search_results,
            "best_deal": best_deal,
            "insider_tips": unique_tips,
            "conversation_history": self.conversation_history
        }
    
    def _generate_summary(self, user_request, trip_data, search_results, best_deal, tips):
        """Generate beautiful recommendation using Claude."""
        
        results_summary = []
        for dest, data in search_results["results"].items():
            results_summary.append({
                "destination": data["destination_city"],
                "country": data["destination_country"],
                "cheapest_price": data["cheapest_price"],
                "flights_available": data["flights_count"],
                "top_flight": data["flights"][0] if data["flights"] else None
            })
        
        tips_text = "\n".join([f"- {tip['tip']}" for tip in tips]) if tips else "No specific tips available."
        
        # Add context if this is a follow-up
        context_note = ""
        if len(self.conversation_history) > 2:
            context_note = "Note: This is part of an ongoing conversation. Reference previous context naturally."
        
        system_prompt = f"""You are FlightSage, a friendly AI travel strategist.

{context_note}

Style:
- Friendly, warm, like a travel-savvy friend
- Use emojis tastefully
- Highlight best deal first
- Compare 2-3 options briefly
- Include 1-2 insider tips naturally
- End with an actionable question

Keep under 250 words."""
        
        prompt = f"""User requested: "{user_request}"

Plan details:
- Budget: ${trip_data.get('budget_max', 'flexible')}
- Trip type: {trip_data.get('trip_type', 'leisure')}
- Preferences: {trip_data.get('preferences', [])}

Flight options found:
{results_summary}

Best deal:
{best_deal if best_deal.get('success') else 'No clear winner'}

INSIDER TIPS (use these!):
{tips_text}

Write a beautiful recommendation."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text


# ============================================================
# TEST IT!
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🎯 ORCHESTRATOR - MULTI-TURN WITH ERROR HANDLING TEST")
    print("=" * 60)
    print()
    
    orchestrator = FlightSageOrchestrator()
    
    # Test 1: Low budget (should show error)
    print("\n" + "=" * 60)
    print("TEST 1: LOW BUDGET ($50)")
    print("=" * 60)
    print("\n👤 USER: Trip under $50")
    result1 = orchestrator.chat("Trip under $50")
    print(f"🤖 AI: {result1['message']}")
    print(f"Type: {result1['type']}")
    
    # Test 2: Valid request
    print("\n" + "=" * 60)
    print("TEST 2: VALID REQUEST")
    print("=" * 60)
    print("\n👤 USER: Beach in March, $800")
    result2 = orchestrator.chat("Beach in March, $800")
    if result2["type"] == "trip_plan":
        print(f"🤖 AI: {result2['summary'][:200]}...")
    else:
        print(f"🤖 AI: {result2['message']}")
    print(f"Type: {result2['type']}")
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")
    print("=" * 60)
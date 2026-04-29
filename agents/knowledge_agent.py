"""
FlightSage - Knowledge Agent (RAG)
The "travel-savvy local friend" that knows insider tips.

This agent uses RAG (Retrieval-Augmented Generation) to:
1. Store travel tips in a vector database (ChromaDB)
2. Search for relevant tips based on user queries
3. Filter results by relevance threshold for quality control
4. Provide context-aware insights
"""

import os
import sys
import json
import chromadb
from chromadb.config import Settings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class KnowledgeAgent:
    """
    The Knowledge Agent uses RAG to provide insider travel tips.
    
    Architecture:
    1. ChromaDB stores travel tips with embeddings
    2. Semantic search finds relevant tips
    3. Quality threshold filters out low-relevance matches
    4. Returns top tips for any query
    """
    
    def __init__(self, db_path: str = "./travel_db"):
        self.name = "Knowledge Agent"
        self.role = "Travel-savvy Local Friend"
        self.db_path = db_path
        
        print(f" Initializing {self.name}...")
        
        # Create ChromaDB client (persistent storage)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="travel_tips",
            metadata={"description": "Travel insider tips and seasonal advice"}
        )
        
        print(f"    Connected to vector database")
        
        # Load tips if database is empty
        if self.collection.count() == 0:
            print("   📚 Database is empty, loading travel tips...")
            self._load_tips_from_json()
        else:
            print(f"    Database has {self.collection.count()} tips loaded")
    
    def _load_tips_from_json(self):
        """Load travel tips from JSON file into ChromaDB."""
        try:
            # Path to travel tips file
            tips_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data",
                "travel_tips.json"
            )
            
            with open(tips_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            tips = data["tips"]
            
            # Add tips to ChromaDB
            self.collection.add(
                documents=[tip["tip"] for tip in tips],
                metadatas=[
                    {
                        "destination": tip["destination"],
                        "category": tip["category"]
                    }
                    for tip in tips
                ],
                ids=[tip["id"] for tip in tips]
            )
            
            print(f"    Loaded {len(tips)} travel tips into vector database")
        
        except Exception as e:
            print(f"    Error loading tips: {e}")
    
    def search(self, query: str, n_results: int = 3, min_relevance: float = 0.3) -> dict:
        """
        Search for relevant travel tips with quality filtering.
        
        Args:
            query: What the user wants to know (e.g., "When to visit Japan")
            n_results: Number of tips to return
            min_relevance: Minimum relevance threshold (0-1). Tips below this 
                          are filtered out. Default 0.3 = 30% relevance.
        
        Returns:
            List of relevant tips with metadata and proper relevance scores
        """
        try:
            # Get more results than needed (we'll filter by quality)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results * 2  # Get extra to filter from
            )
            
            # Format the results with proper relevance scoring
            tips = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    # Get distance from ChromaDB
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    
                    # Convert distance to relevance score (0-1 scale)
                    # ChromaDB distances can be 0-2, we normalize to 0-1
                    # Lower distance = higher relevance
                    relevance = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                    
                    # Only keep tips above the relevance threshold
                    if relevance >= min_relevance:
                        tips.append({
                            "tip": doc,
                            "destination": results["metadatas"][0][i]["destination"],
                            "category": results["metadatas"][0][i]["category"],
                            "relevance_score": relevance
                        })
                
                # Limit to n_results after filtering
                tips = tips[:n_results]
            
            return {
                "success": True,
                "query": query,
                "tips_count": len(tips),
                "tips": tips
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_destination_tips(self, destination: str, n_results: int = 5, min_relevance: float = 0.3) -> dict:
        """
        Get all tips for a specific destination.
        
        Args:
            destination: Destination name (e.g., "Japan", "Mexico")
            n_results: Maximum number of tips to return
            min_relevance: Minimum relevance threshold (0-1)
        
        Returns:
            Tips filtered by destination and relevance
        """
        return self.search(
            f"travel tips for {destination}", 
            n_results=n_results,
            min_relevance=min_relevance
        )


# ============================================================
# TEST IT!
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" KNOWLEDGE AGENT - TEST (with relevance filtering)")
    print("=" * 60)
    print()
    
    # Initialize the agent
    agent = KnowledgeAgent()
    
    print()
    print("=" * 60)
    print("Running test queries with relevance filtering...")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "When should I visit Japan?",
        "How can I save money on flights?",
        "Best time to go to Mexico for a warm beach trip",
        "Romantic destinations under $1500",
        "Adventure travel ideas",
        "When is cherry blossom season?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: \"{query}\"")
        print("-" * 60)
        
        results = agent.search(query, n_results=3, min_relevance=0.3)
        
        if results["success"]:
            if results["tips_count"] == 0:
                print("     No tips above 30% relevance threshold")
            else:
                for j, tip in enumerate(results["tips"], 1):
                    print(f"   Tip {j} ({tip['destination']} - {tip['category']}):")
                    print(f"     {tip['tip']}")
                    print(f"     [Relevance: {tip['relevance_score']:.0%}]")
                    print()
    
    print("=" * 60)
    print(" Knowledge Agent (RAG) is working with quality filtering!")
    print("=" * 60)
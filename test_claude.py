import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load API key from .env file
load_dotenv()

# Create Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Send a test message to Claude
print("🤖 Testing Claude connection...")
print("-" * 50)

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": "I'm building FlightSage, an AI travel strategist. In 3 short bullet points, explain why an AI travel agent is better than Google Flights."
        }
    ]
)

# Print Claude's response
print(response.content[0].text)
print("-" * 50)
print("✅ Test successful! Claude is connected!")
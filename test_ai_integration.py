"""
Test script for AI integration.

Run this to test the Groq API and LangChain agent.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai import get_task_agent, get_groq_client
from ai.parsers import parse_datetime, extract_priority, infer_category


def test_parsers():
    """Test rule-based parsers."""
    print("=" * 60)
    print("Testing Rule-Based Parsers")
    print("=" * 60)
    
    # Test datetime parsing
    print("\n1. DateTime Parsing:")
    test_dates = [
        "tomorrow at 5pm",
        "next Friday",
        "in 2 hours",
        "January 15th"
    ]
    for date_str in test_dates:
        result = parse_datetime(date_str)
        print(f"   '{date_str}' → {result}")
    
    # Test priority extraction
    print("\n2. Priority Extraction:")
    test_texts = [
        "This is urgent!",
        "Low priority task",
        "Just a normal task"
    ]
    for text in test_texts:
        priority = extract_priority(text)
        print(f"   '{text}' → {priority}")
    
    # Test category inference
    print("\n3. Category Inference:")
    test_texts = [
        "Buy groceries at the store",
        "Finish the work report",
        "Call mom",
        "Pay the electricity bill"
    ]
    for text in test_texts:
        category = infer_category(text)
        print(f"   '{text}' → {category}")


def test_groq_client():
    """Test Groq API client."""
    print("\n" + "=" * 60)
    print("Testing Groq API Client")
    print("=" * 60)
    
    try:
        groq = get_groq_client()
        print("✅ Groq client initialized successfully")
        
        # Test task parsing
        print("\n1. Task Parsing:")
        test_inputs = [
            "Buy groceries tomorrow at 5pm, it's urgent",
            "Finish the project report by Friday end of day",
            "Call dentist to schedule appointment"
        ]
        
        for nl_input in test_inputs:
            print(f"\n   Input: '{nl_input}'")
            try:
                result = groq.parse_task_from_nl(nl_input)
                print(f"   Output: {result}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Test search query parsing
        print("\n2. Search Query Parsing:")
        test_queries = [
            "Show me all high priority tasks",
            "What tasks are completed?",
            "Find tasks about groceries"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                result = groq.search_query_to_filters(query)
                print(f"   Filters: {result}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n✅ Groq API tests completed")
        
    except Exception as e:
        print(f"\n❌ Groq client error: {str(e)}")
        print("   Make sure GROQ_API_KEY is set in your .env file")


def test_task_agent():
    """Test LangChain task agent."""
    print("\n" + "=" * 60)
    print("Testing LangChain Task Agent")
    print("=" * 60)
    
    try:
        agent = get_task_agent()
        print("✅ Task agent initialized successfully")
        
        # Test natural language task parsing
        print("\n1. Natural Language Task Parsing:")
        test_inputs = [
            "Remind me to buy milk tomorrow",
            "Schedule team meeting next Monday at 2pm, high priority",
            "Pay rent by the 5th"
        ]
        
        for nl_input in test_inputs:
            print(f"\n   Input: '{nl_input}'")
            try:
                result = agent.parse_task_nl(nl_input)
                print(f"   Parsed: {result}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Test search
        print("\n2. Natural Language Search:")
        test_queries = [
            "Show pending tasks",
            "Find urgent items",
            "What's due today?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                result = agent.search_tasks_nl(query)
                print(f"   Filters: {result}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n✅ Task agent tests completed")
        
    except Exception as e:
        print(f"\n❌ Task agent error: {str(e)}")


def main():
    """Run all tests."""
    print("\n🧪 MCP Todo - AI Integration Tests\n")
    
    # Test parsers (no API required)
    test_parsers()
    
    # Test Groq API (requires API key)
    test_groq_client()
    
    # Test task agent (requires API key)
    test_task_agent()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

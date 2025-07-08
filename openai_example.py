import os
from openai import OpenAI
from typing import List, Dict
import asyncio

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_story(prompt: str, max_tokens: int = 500) -> str:
    """
    Generate a creative story using OpenAI's API.
    
    Args:
        prompt: The story prompt to start with
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        str: The generated story
    """
    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=f"Write a creative story based on this prompt: {prompt}",
            max_tokens=max_tokens,
            temperature=0.8
        )
        return response.output_text
    except Exception as e:
        return f"Error generating story: {str(e)}"

def analyze_sentiment(texts: List[str]) -> List[Dict[str, str]]:
    """
    Analyze sentiment of multiple texts using OpenAI.
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of sentiment analysis results
    """
    results = []
    
    for text in texts:
        try:
            response = client.responses.create(
                model="gpt-4.1",
                input=f"Analyze the sentiment of this text and respond with only one word: POSITIVE, NEGATIVE, or NEUTRAL\n\nText: {text}",
                max_tokens=10,
                temperature=0
            )
            sentiment = response.output_text.strip()
            results.append({"text": text[:50] + "...", "sentiment": sentiment})
        except Exception as e:
            results.append({"text": text[:50] + "...", "error": str(e)})
    
    return results

def use_web_search(query: str) -> str:
    """
    Example of using OpenAI's web search tool.
    
    Args:
        query: The search query
        
    Returns:
        str: The search results
    """
    try:
        response = client.responses.create(
            model="gpt-4.1",
            tools=[{"type": "web_search_preview"}],
            input=query
        )
        return response.output_text
    except Exception as e:
        return f"Error with web search: {str(e)}"

async def stream_response(prompt: str):
    """
    Stream a response from OpenAI.
    
    Args:
        prompt: The prompt to generate from
    """
    try:
        stream = client.responses.create(
            model="gpt-4.1",
            input=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        full_response = ""
        for event in stream:
            if hasattr(event, 'output_text'):
                chunk = event.output_text
                full_response += chunk
                print(chunk, end='', flush=True)
        
        return full_response
    except Exception as e:
        return f"Error streaming: {str(e)}"

def analyze_image(image_url: str, question: str) -> str:
    """
    Analyze an image using OpenAI's vision capabilities.
    
    Args:
        image_url: URL of the image to analyze
        question: Question about the image
        
    Returns:
        str: Analysis result
    """
    try:
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "user", "content": question},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": image_url
                        }
                    ]
                }
            ]
        )
        return response.output_text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

if __name__ == "__main__":
    # Example usage
    print("1. Story Generation:")
    story = generate_story("A robot discovers emotions for the first time")
    print(story[:200] + "...\n")
    
    print("2. Sentiment Analysis:")
    sentiments = analyze_sentiment([
        "This product exceeded all my expectations!",
        "The service was terrible and slow.",
        "The weather today is cloudy."
    ])
    for result in sentiments:
        print(f"  - {result}\n")
    
    print("3. Web Search Example:")
    search_result = use_web_search("What are the latest AI breakthroughs in 2024?")
    print(search_result[:200] + "...\n")
    
    print("4. Streaming Example:")
    print("Streaming response: ")
    asyncio.run(stream_response("Tell me a joke about programming"))
    print("\n")
    
    print("5. Image Analysis:")
    image_result = analyze_image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GoldenGateBridge-001.jpg/1200px-GoldenGateBridge-001.jpg",
        "What landmark is shown in this image?"
    )
    print(image_result)
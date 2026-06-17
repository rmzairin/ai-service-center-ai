import os
import requests
from dotenv import load_dotenv

load_dotenv()

LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://ai-service-center-web.test")


def get_all_knowledge() -> list:
    try:
        response = requests.get(f"{LARAVEL_API_URL}/api/knowledge-active", timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result.get("data", [])

        return []

    except Exception as e:
        print(f"Error fetching knowledge: {e}")
        return []


def retrieve_context(query: str, top_k: int = 5) -> list:
    knowledge_list = get_all_knowledge()
    query_lower = query.lower()

    matches = []

    for item in knowledge_list:
        score = 0

        question_lower = item["question"].lower()
        if any(word in question_lower for word in query_lower.split()):
            score += 2

        if item.get("keywords"):
            keywords_lower = item["keywords"].lower()
            for word in query_lower.split():
                if word in keywords_lower:
                    score += 3

        if score > 0:
            matches.append({"item": item, "score": score})

    matches.sort(key=lambda x: x["score"], reverse=True)
    return [m["item"] for m in matches[:top_k]]
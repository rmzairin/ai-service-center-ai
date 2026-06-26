import os
import fitz
import requests
from dotenv import load_dotenv
from services.rag_service import filter_query_words, fuzzy_match, translate_to_id

load_dotenv()

LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://ai-service-center-web.test")


def get_all_documents() -> list:
    try:
        response = requests.get(f"{LARAVEL_API_URL}/api/documents-processed", timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("data", [])
        return []
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []


def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        return full_text.strip()
    except Exception as e:
        print(f"Error extracting PDF {file_path}: {e}")
        return ""


def split_into_chunks(text: str, chunk_size: int = 100) -> list:
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def retrieve_from_documents(query: str, top_k: int = 3) -> list:
    documents = get_all_documents()

    # Translate + filter kata bermakna
    translated_query = translate_to_id(query)
    original_words = filter_query_words(query)
    translated_words = filter_query_words(translated_query)
    query_words = list(set(original_words + translated_words))

    print(f"DEBUG DOC - Query words: {query_words}")

    if not query_words:
        return []

    matches = []

    for doc in documents:
        file_path = doc.get("file_path", "")

        if not file_path or not os.path.exists(file_path):
            continue

        full_text = extract_text_from_pdf(file_path)
        if not full_text:
            continue

        chunks = split_into_chunks(full_text, chunk_size=100)

        for chunk in chunks:
            chunk_words = chunk.lower().split()
            score = 0

            for qword in query_words:
                # Exact match
                if qword in chunk_words:
                    score += 2
                else:
                    # Fuzzy match
                    for cw in chunk_words:
                        if fuzzy_match(qword, cw, threshold=80):
                            score += 1
                            break

            if score >= 2:
                matches.append({
                    "text"     : chunk,
                    "score"    : score,
                    "source"   : doc["title"],
                    "file_name": doc["file_name"],
                })

    matches.sort(key=lambda x: x["score"], reverse=True)
    print(f"DEBUG DOC - Total matches: {len(matches)}")
    if matches:
        print(f"DEBUG DOC - Best score: {matches[0]['score']}")
        print(f"DEBUG DOC - Best chunk: {matches[0]['text'][:80]}")

    return matches[:top_k]
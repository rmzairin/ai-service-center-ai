import os
import requests
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from deep_translator import GoogleTranslator
from services.intent_service import detect_question_type, detect_answer_type

load_dotenv()

LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://ai-service-center-web.test")

STOP_WORDS = {
    "apa", "itu", "ini", "yang", "dan", "di", "ke", "dari", "untuk",
    "dengan", "adalah", "ada", "tidak", "bisa", "cara", "bagaimana",
    "berapa", "siapa", "kapan", "dimana", "kenapa", "mengapa", "apakah",
    "nya", "saya", "kamu", "kami", "kita", "mereka", "dia", "anda",
    "ya", "dong", "deh", "sih", "kok", "kan", "lah", "yg", "yah",
    "dimaksud", "maksud", "jelaskan", "tolong", "mohon", "sebutkan",
    "tentang", "mengenai", "terkait", "gimana", "pengertian",
    "definisi", "arti", "the", "is", "of", "and", "or", "in", "a",
    "an", "to", "what", "how", "why", "when", "where", "who"
}


def translate_to_id(text: str) -> str:
    """
    Terjemahkan teks ke Bahasa Indonesia.
    Kalau gagal, kembalikan teks asli.
    Analogi Laravel: seperti middleware yang transform request sebelum diproses
    """
    try:
        translated = GoogleTranslator(source='auto', target='id').translate(text)
        print(f"DEBUG TRANSLATE - '{text}' → '{translated}'")
        return translated
    except Exception as e:
        print(f"DEBUG TRANSLATE - Gagal: {e}, pakai teks asli")
        return text


def filter_query_words(query: str) -> list:
    """
    Pecah query jadi kata-kata bermakna, buang stop words.
    """
    words = query.lower().split()
    return [
        word.strip("?.,!") for word in words
        if word.strip("?.,!") not in STOP_WORDS
        and len(word.strip("?.,!")) > 2
    ]


def fuzzy_match(word: str, target: str, threshold: int = 75) -> bool:
    """
    Cek apakah 2 kata mirip (toleransi typo).
    Threshold 75 = minimal 75% kemiripan.
    Contoh: "maping" vs "mapping" → 88% → match ✅
             "obat" vs "apotek" → 40% → tidak match ❌
    """
    return fuzz.ratio(word, target) >= threshold


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

    translated_query = translate_to_id(query)
    original_words = filter_query_words(query)
    translated_words = filter_query_words(translated_query)
    query_words = list(set(original_words + translated_words))

    # Deteksi tipe pertanyaan user
    question_type = detect_question_type(query)
    print(f"DEBUG KB - Question type: {question_type}")
    print(f"DEBUG KB - Query words: {query_words}")

    if not query_words:
        return []

    matches = []

    for item in knowledge_list:
        score = 0
        matched_words = set()

        question_words = item["question"].lower().split()

        for qword in query_words:
            if qword in question_words:
                score += 2
                matched_words.add(qword)
            else:
                for qw in question_words:
                    if fuzzy_match(qword, qw):
                        score += 1
                        matched_words.add(qword)
                        break

        if item.get("keywords"):
            keyword_list = [k.strip().lower() for k in item["keywords"].split(",")]
            for qword in query_words:
                if qword in keyword_list:
                    score += 3
                    matched_words.add(qword)
                else:
                    for kw in keyword_list:
                        if fuzzy_match(qword, kw):
                            score += 2
                            matched_words.add(qword)
                            break

        coverage = len(matched_words) / len(query_words) if query_words else 0

        # Deteksi tipe jawaban KB
        answer_type = detect_answer_type(item["answer"])

        # Kalau tipe pertanyaan BUKAN "umum", pastikan tipe jawaban sesuai
        if question_type != "umum" and answer_type != "umum":
            if question_type != answer_type:
                print(f"DEBUG KB - SKIP '{item['question'][:35]}' (tanya {question_type}, jawaban {answer_type})")
                continue

        print(f"DEBUG KB - '{item['question'][:35]}' | Score: {score} | Coverage: {coverage:.0%} | Q-type: {question_type} | A-type: {answer_type}")

        if score >= 3 and coverage >= 0.75:
            matches.append({
                "item"    : item,
                "score"   : score,
                "coverage": coverage,
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:top_k]
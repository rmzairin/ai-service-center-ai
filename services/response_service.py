from services.intent_service import detect_intent
from services.rag_service import retrieve_context


def generate_response(message: str, session_id: int) -> dict:
    intent = detect_intent(message)

    # Cari knowledge yang relevan
    results = retrieve_context(message)

    if results:
        # Ambil jawaban dari knowledge dengan score tertinggi
        best_match = results[0]

        return {
            "answer": best_match["answer"],
            "confidence": 0.8,
            "tokens_used": None,
            "model_name": "rag-keyword-v1"
        }

    # Kalau tidak ada yang cocok
    if intent == "greeting":
        answer = "Halo! Ada yang bisa saya bantu?"
    elif intent == "thanks":
        answer = "Sama-sama! Senang bisa membantu."
    else:
        answer = "Maaf, saya belum menemukan jawaban untuk pertanyaan Anda. Tim kami akan membantu lebih lanjut."

    return {
        "answer": answer,
        "confidence": 0.3,
        "tokens_used": None,
        "model_name": "rag-keyword-v1"
    }
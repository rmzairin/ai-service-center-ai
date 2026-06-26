from services.intent_service import detect_intent, detect_answer_length
from services.rag_service import retrieve_context
from services.document_service import retrieve_from_documents


def format_answer(text: str, length: str) -> str:
    text = text.strip()
    if length == "short":
        if len(text) > 150:
            cutoff = text[:150]
            last_period = max(cutoff.rfind('.'), cutoff.rfind(','))
            if last_period > 80:
                return cutoff[:last_period + 1]
            return cutoff + "..."
        return text
    elif length == "long":
        return text
    else:
        if len(text) > 400:
            cutoff = text[:400]
            last_period = max(cutoff.rfind('.'), cutoff.rfind(','))
            if last_period > 200:
                return cutoff[:last_period + 1]
            return cutoff + "..."
        return text


def generate_response(message: str, session_id: int) -> dict:
    intent = detect_intent(message)
    answer_length = detect_answer_length(message)

    print(f"DEBUG - Intent: {intent} | Answer length: {answer_length}")

    # 1. Cari di Knowledge Base
    kb_results = retrieve_context(message)
    kb_score = kb_results[0]["score"] if kb_results else 0
    print(f"DEBUG - Best KB score: {kb_score}")

    # 2. Cari di dokumen PDF
    doc_results = retrieve_from_documents(message)
    doc_score = doc_results[0]["score"] if doc_results else 0
    print(f"DEBUG - Best DOC score: {doc_score}")

    # 3. Pilih sumber dengan score tertinggi
    # KB menang hanya kalau score-nya lebih tinggi ATAU sama dengan dokumen
    if kb_score > 0 and kb_score >= doc_score:
        best_kb = kb_results[0]["item"]
        print(f"DEBUG - Pakai KB: {best_kb['answer'][:50]}")
        return {
            "answer"     : format_answer(best_kb["answer"], answer_length),
            "confidence" : 0.85,
            "tokens_used": None,
            "model_name" : "rag-keyword-kb-v1"
        }

    if doc_score > 0:
        best_chunk = doc_results[0]
        raw_answer = f"Dari dokumen '{best_chunk['source']}':\n{best_chunk['text'].strip()}"
        print(f"DEBUG - Pakai DOC: {best_chunk['text'][:50]}")
        return {
            "answer"     : format_answer(raw_answer, answer_length),
            "confidence" : 0.65,
            "tokens_used": None,
            "model_name" : "rag-keyword-doc-v1"
        }

    # 4. Fallback
    if intent == "greeting":
        answer = "Halo! Ada yang bisa saya bantu?"
    elif intent == "thanks":
        answer = "Sama-sama! Senang bisa membantu."
    else:
        from services.rag_service import filter_query_words
        keywords = filter_query_words(message)
        topic = ", ".join(keywords[:3]) if keywords else "pertanyaan Anda"
        answer = f"Maaf, saya tidak menemukan informasi mengenai '{topic}' di sistem kami. Silakan hubungi tim kami secara langsung untuk bantuan lebih lanjut."

    return {
        "answer"     : answer,
        "confidence" : 0.0,
        "tokens_used": None,
        "model_name" : "fallback"
    }
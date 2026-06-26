def detect_intent(message: str) -> str:
    message_lower = message.lower()

    if any(word in message_lower for word in ["halo", "hai", "hi", "hello"]):
        return "greeting"
    elif any(word in message_lower for word in ["terima kasih", "thanks", "makasih"]):
        return "thanks"
    elif "?" in message:
        return "question"
    else:
        return "general"


def detect_answer_length(message: str) -> str:
    """
    Deteksi apakah user minta jawaban singkat atau detail.
    Return: "short" atau "long"
    """
    message_lower = message.lower()

    # Kata-kata yang menandakan minta jawaban SINGKAT
    short_keywords = [
        "singkat", "ringkas", "pendek", "padat", "sebentar",
        "simpel", "simple", "brief", "summary", "intinya",
        "pokoknya", "inti", "garis besar", "secara singkat",
        "secara ringkas", "cukup", "saja", "aja"
    ]

    # Kata-kata yang menandakan minta jawaban DETAIL/PANJANG
    long_keywords = [
        "detail", "lengkap", "panjang", "jelaskan", "dijelaskan",
        "elaborasi", "mendalam", "komprehensif", "menyeluruh",
        "secara lengkap", "secara detail", "lebih lanjut",
        "lebih dalam", "semua", "seluruh"
    ]

    if any(word in message_lower for word in short_keywords):
        return "short"
    elif any(word in message_lower for word in long_keywords):
        return "long"
    else:
        return "medium"  # default: sedang
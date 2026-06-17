def detect_intent(message: str) -> str:
    """
    Placeholder deteksi intent.
    Nanti bisa diganti dengan classifier model.
    """
    message_lower = message.lower()

    if any(word in message_lower for word in ["halo", "hai", "hi", "hello"]):
        return "greeting"
    elif any(word in message_lower for word in ["terima kasih", "thanks"]):
        return "thanks"
    elif "?" in message:
        return "question"
    else:
        return "general"
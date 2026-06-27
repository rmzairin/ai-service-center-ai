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
    
def detect_question_type(message: str) -> str:
    """
    Deteksi tipe pertanyaan user.
    Ini lebih reliable dari manual time_words list.
    """
    message_lower = message.lower()

    # Tipe WAKTU: tanya jam/jadwal/kapan
    if any(w in message_lower for w in [
        "jam berapa", "pukul berapa", "jadwal", "kapan", "hari apa",
        "jam praktek", "jam buka", "jam tutup", "what time", "when",
        "jam datang", "jam pelayanan", "jam operasional"
    ]):
        return "waktu"

    # Tipe IDENTITAS: tanya nama/siapa
    if any(w in message_lower for w in [
        "nama", "siapa", "who is", "nama lengkap", "nama dokter",
        "nama direktur", "nama kepala", "nama petugas"
    ]):
        return "identitas"

    # Tipe LOKASI: tanya tempat/dimana
    if any(w in message_lower for w in [
        "dimana", "lokasi", "alamat", "ruangan", "lantai",
        "where", "gedung", "tempat", "letak"
    ]):
        return "lokasi"

    # Tipe PROSEDUR: tanya cara/bagaimana
    if any(w in message_lower for w in [
        "bagaimana", "cara", "langkah", "prosedur", "how to",
        "gimana", "caranya", "tahapan", "alur"
    ]):
        return "prosedur"

    # Tipe DEFINISI: tanya pengertian/apa itu
    if any(w in message_lower for w in [
        "apa itu", "apa yang", "pengertian", "definisi", "maksud",
        "arti", "what is", "jelaskan", "apa itu"
    ]):
        return "definisi"

    # Tipe SYARAT: tanya persyaratan
    if any(w in message_lower for w in [
        "syarat", "persyaratan", "dokumen", "perlu", "harus bawa",
        "requirement", "ketentuan"
    ]):
        return "syarat"

    return "umum"


def detect_answer_type(answer: str) -> str:
    """
    Deteksi tipe jawaban dari KB.
    """
    answer_lower = answer.lower()

    if any(w in answer_lower for w in ["pukul", "jam", "hari", "senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu", "wita", "wib"]):
        return "waktu"

    if any(w in answer_lower for w in ["dr.", "dokter", "nama", "sp.", "prof.", "bapak", "ibu", "direktur"]):
        return "identitas"

    if any(w in answer_lower for w in ["jl.", "jalan", "lantai", "ruang", "gedung", "alamat", "lokasi"]):
        return "lokasi"

    if any(w in answer_lower for w in ["langkah", "cara", "pertama", "kedua", "ketiga", "1.", "2.", "3."]):
        return "prosedur"

    if any(w in answer_lower for w in ["ktp", "kartu", "surat", "bawa", "dokumen", "syarat", "wajib"]):
        return "syarat"

    return "umum"
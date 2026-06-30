# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerRegistry
from presidio_analyzer.nlp_engine import SlimSpacyNlpEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer

SUPPORTED_LANGUAGE = "vi"


def _build_name_recognizer() -> PatternRecognizer:
    """Recognizer cho tên người Việt (2+ từ, hỗ trợ dấu)."""
    name_pattern = Pattern(
        name="vn_person",
        regex=r"[A-Za-zÀ-ỹà-ỹĐđ]+(?:\s+[A-Za-zÀ-ỹà-ỹĐđ]+)+",
        score=0.75,
    )
    return PatternRecognizer(
        supported_entity="PERSON",
        supported_language=SUPPORTED_LANGUAGE,
        patterns=[name_pattern],
        context=["họ tên", "bệnh nhân", "tên", "bác sĩ"],
    )


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN.
    Dùng SlimSpacyNlpEngine (blank tokenizer) để tránh phụ thuộc model lớn.
    """
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language=SUPPORTED_LANGUAGE,
        patterns=[Pattern(name="cccd_pattern", regex=r"\d{12}", score=0.9)],
        context=["cccd", "căn cước", "chứng minh", "cmnd"],
    )

    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language=SUPPORTED_LANGUAGE,
        patterns=[
            Pattern(name="vn_phone", regex=r"0?[35789]\d{8}", score=0.85)
        ],
        context=["điện thoại", "sdt", "phone", "liên hệ"],
    )

    name_recognizer = _build_name_recognizer()
    email_recognizer = EmailRecognizer(supported_language=SUPPORTED_LANGUAGE)

    registry = RecognizerRegistry(
        recognizers=[
            cccd_recognizer,
            phone_recognizer,
            name_recognizer,
            email_recognizer,
        ],
        supported_languages=[SUPPORTED_LANGUAGE],
    )

    nlp_engine = SlimSpacyNlpEngine(
        supported_languages=[SUPPORTED_LANGUAGE],
        generic_tokenizer="blank",
        auto_download=False,
    )

    return AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine,
        supported_languages=[SUPPORTED_LANGUAGE],
    )


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    """
    results = analyzer.analyze(
        text=text,
        language=SUPPORTED_LANGUAGE,
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
    return results

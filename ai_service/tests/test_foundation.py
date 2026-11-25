from ai_service.app.config import (
    APP_NAME, APP_VERSION, REQUEST_TIMEOUT,
    GOOGLE_NEWS_MAX_RESULTS, BM25_TOP_K, OCR_LANGUAGE,
)
from ai_service.app.utils.logging_config import setup_logging, get_logger

def test_foundation():
    setup_logging()
    logger = get_logger("truthcams.test")
    assert APP_NAME == "Truthcams AI"
    assert APP_VERSION == "0.1.0"
    assert REQUEST_TIMEOUT > 0
    assert GOOGLE_NEWS_MAX_RESULTS > 0
    assert BM25_TOP_K > 0
    assert OCR_LANGUAGE == "vie+eng"
    logger.info("Foundation test passed")

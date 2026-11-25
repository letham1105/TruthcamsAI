from ai_service.app.input.input_processor import process_input

def test_text_input():
    result = process_input("  Tin thử nghiệm tiếng Việt  ", "text")
    assert result["extracted_text"] == "Tin thử nghiệm tiếng Việt"
    assert result["metadata"]["status"] == "success"

def test_empty_text():
    result = process_input("   ", "text")
    assert result["metadata"]["status"] == "failed"
    assert result["extracted_text"] == ""

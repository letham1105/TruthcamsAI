
import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


# 1. Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")


# 2. Initialize Gemini client
client = genai.Client(api_key=API_KEY)


# 3. Sample input for Truthcams AI
sample_text = """
Ngày 15/11/2026, thành phố Đà Nẵng công bố
kế hoạch xây dựng thêm 5 cây cầu mới trong
giai đoạn 2027-2030.

Thông tin này được chia sẻ trên mạng xã hội.
"""


# 4. Define extraction prompt
prompt = f"""
Bạn là hệ thống trích xuất claim cho ứng dụng
kiểm chứng thông tin Truthcams AI.

Nhiệm vụ:
- Đọc văn bản được cung cấp.
- Trích xuất các phát biểu có thể kiểm chứng.
- Không tự bổ sung thông tin bên ngoài văn bản.
- Không kết luận thông tin đúng hay sai.
- Nếu không có claim phù hợp, trả về danh sách rỗng.

Trả về JSON hợp lệ theo cấu trúc:

{{
    "claims": [
        {{
            "claim_id": "C1",
            "claim_text": "Nội dung phát biểu",
            "claim_type": "announcement",
            "entities": [
                {{
                    "name": "Tên thực thể",
                    "type": "LOCATION"
                }}
            ],
            "temporal": {{
                "date": "2026-11-15"
            }}
        }}
    ]
}}

Văn bản đầu vào:
{sample_text}
"""


# 5. Send request to Gemini
print("=" * 60)
print("TRUTHCAMS AI - GEMINI API TEST")
print("=" * 60)

print(f"Model: {MODEL}")
print("Sending request...\n")

try:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    result_text = response.text

    print("RAW RESPONSE:")
    print("-" * 60)
    print(result_text)

    # 6. Validate JSON
    result = json.loads(result_text)

    print("\nJSON VALIDATION:")
    print("-" * 60)
    print("Valid JSON:", isinstance(result, dict))
    print("Number of claims:", len(result.get("claims", [])))

    print("\nEXTRACTED CLAIMS:")
    print("-" * 60)

    for claim in result.get("claims", []):
        print(json.dumps(claim, ensure_ascii=False, indent=2))

    # 7. Token usage
    print("\nTOKEN USAGE:")
    print("-" * 60)

    usage = response.usage_metadata

    if usage:
        print("Input tokens:", usage.prompt_token_count)
        print("Output tokens:", usage.candidates_token_count)
        print("Total tokens:", usage.total_token_count)
    else:
        print("Usage metadata unavailable.")

    print("\nTEST COMPLETED.")

except Exception as error:
    print("\nGEMINI API ERROR:")
    print(type(error).__name__)
    print(str(error))

# TruthCams AI

## Source Code & Developer Guide

Tài liệu dành cho thành viên phát triển và người mới tiếp cận source code. Nội dung tập trung vào kiến trúc, các module chính, API, cài đặt và vận hành local.

> **Phạm vi:** Hướng dẫn được tổng hợp từ source code đã cung cấp. Những phần chưa xác minh được ghi rõ để tránh nhầm lẫn với chức năng đã triển khai.

## Nội dung

1. [Tổng quan](#1-tổng-quan-dự-án)
2. [Kiến trúc](#2-kiến-trúc-hệ-thống)
3. [Cấu trúc source code](#3-cấu-trúc-thư-mục-và-trách-nhiệm-file)
4. [AI pipeline](#4-chi-tiết-luồng-ai-pipeline)
5. [API](#5-backend-api-documentation)
6. [Database](#6-database)
7. [Cài đặt](#7-cài-đặt-dependencies)
8. [Cấu hình môi trường](#8-cấu-hình-môi-trường)
9. [Chạy dự án](#9-cách-chạy-dự-án-từ-đầu)
10. [Kiểm thử và xử lý lỗi](#10-kiểm-thử)
11. [Các điểm cần cải thiện](#12-những-điểm-chưa-đồng-nhất--cần-cải-thiện)
12. [Giới hạn và bảo mật](#13-giới-hạn-khi-diễn-giải-kết-quả)

---

## 1. Tổng quan dự án

TruthCams AI nhận văn bản, hình ảnh hoặc URL; trích xuất claims; tìm bài báo liên quan; truy xuất evidence; dự đoán quan hệ claim–evidence; sau đó tổng hợp kết quả và lưu phiên phân tích.

### 1.1. Các thành phần chính

| Thành phần | Công nghệ / vai trò |
|---|---|
| Frontend | React, TypeScript, Vite, React Router, Axios, Tailwind CSS |
| Backend API | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL (theo driver `psycopg[binary]` trong requirements) |
| AI pipeline | Python; xử lý input, claim extraction, search, retrieval, verification |
| Claim extraction | Code hiện được cung cấp gọi Gemini qua `google-genai` |
| News search | Google News RSS |
| Article extraction | Requests, BeautifulSoup, lxml, Trafilatura (nếu cài) |
| Retrieval | BM25 (`rank_bm25`), tokenizer tiếng Việt `underthesea` (có fallback) |
| Relevance filtering | scikit-learn TF-IDF ký tự và cosine similarity |
| Evidence verification | Hugging Face Transformers, PyTorch, checkpoint VELECTRA cục bộ |
| OCR | Tesseract OCR, pytesseract, Pillow |
| Authentication | Password hashing Argon2 qua `pwdlib`, JWT |
| Database migrations | Alembic |

### 1.2. Phạm vi hỗ trợ của input

- **Text:** văn bản người dùng nhập.
- **Image:** ảnh được OCR thành văn bản.
- **URL:** tải trang HTTP/HTTPS và trích xuất nội dung trang; backend `/analyze` tự nhận diện chuỗi URL thông qua `is_http_url`.
- Endpoint OCR riêng nhận file ảnh; endpoint analyze nhận trường `text`.

---

## 2. Kiến trúc hệ thống

```mermaid
flowchart LR
    U([Người dùng]) --> FE["Frontend<br/>React + TypeScript"]
    FE -->|"REST API"| BE["Backend<br/>FastAPI"]
    BE --> DB[("PostgreSQL")]
    BE --> AI["AI pipeline<br/>Python"]

    subgraph INPUT["1. Tiếp nhận đầu vào"]
        AI --> IN["Text / Image / URL"]
        IN --> OCR["OCR hoặc trích xuất URL"]
        OCR --> CL["Trích xuất claims<br/>Gemini"]
    end

    subgraph SEARCH["2. Tìm kiếm evidence"]
        CL --> Q["Sinh search queries"]
        Q --> GN["Google News RSS"]
        GN --> AR["Làm sạch và trích xuất<br/>bài báo"]
        AR --> P["Chia paragraph"]
        P --> BM["BM25 retrieval"]
    end

    subgraph VERIFY["3. Đánh giá evidence"]
        BM --> REL["Lọc relevance"]
        REL --> VE["VELECTRA"]
        VE --> AG["Tổng hợp verdict"]
    end

    AG --> BE
    BE -->|"Lưu phiên / trả kết quả"| DB
    BE --> FE
```

**Lưu ý kiến trúc:** `ai_service` hiện được backend import trực tiếp như một Python package, không phải HTTP service độc lập. Khi chạy local, chỉ cần khởi động backend và frontend.

### 2.1. Luồng request tổng quát

1. Frontend gửi request đến `http://localhost:8000/api/v1`.
2. FastAPI endpoint validate request bằng Pydantic schema.
3. Endpoint gọi service tương ứng.
4. Verification service tạo bản ghi phiên phân tích ở trạng thái `processing`.
5. Service gọi `run_search_pipeline(...)`.
6. Pipeline trả kết quả và trạng thái `success`, `partial` hoặc `failed`.
7. Service cập nhật bản ghi trong database.
8. API trả session cho frontend.
9. Frontend hiển thị kết quả và cho phép xem lại lịch sử/chi tiết phiên.

**Lưu ý:** Pipeline được gọi đồng bộ trong request theo code đã cung cấp. Chưa có bằng chứng về background worker hoặc queue riêng. Request có thể kéo dài khi phải gọi LLM, Google News và tải nhiều bài báo.

---

## 3. Cấu trúc thư mục và trách nhiệm file

Cấu trúc dưới đây tổng hợp các thư mục/file đã được cung cấp. Một số thư mục frontend được rút gọn vì chưa có toàn bộ danh sách file.

```text
truthcams-ai/
├── .env.example
├── alembic.ini
├── ai_service/
│   ├── requirements.txt
│   ├── test_ai.py
│   ├── models/
│   │   └── velectra-vifactcheck/
│   │       ├── config.json
│   │       ├── model.safetensors
│   │       ├── tokenizer_config.json
│   │       ├── special_tokens_map.json
│   │       ├── vocab.txt
│   │       ├── training_args.bin
│   │       ├── aggregate_metrics.json
│   │       └── artifacts/
│   └── app/
│       ├── config.py
│       ├── pipeline.py
│       ├── extraction/
│       │   ├── claim_extractor.py
│       │   ├── claim_schema.py
│       │   ├── json_parser.py
│       │   ├── model_loader.py
│       │   └── prompts/
│       │       └── claim_extraction.txt
│       ├── input/
│       │   ├── input_processor.py
│       │   ├── ocr.py
│       │   ├── ocr_cleaner.py
│       │   └── url_extractor.py
│       ├── llm/
│       │   └── gemini_provider.py
│       ├── search/
│       │   ├── google_news.py
│       │   ├── query_generator.py
│       │   ├── result_normalizer.py
│       │   ├── url_resolver.py
│       │   ├── article_extractor.py
│       │   ├── article_cleaner.py
│       │   ├── paragraph_segmenter.py
│       │   └── bm25_retriever.py
│       ├── verification/
│       │   ├── verifier.py
│       │   ├── verification_schema.py
│       │   ├── evidence_relevance.py
│       │   ├── evidence_verification.py
│       │   ├── evidence_aggregator.py
│       │   └── README.md
│       ├── visual_search/
│       │   └── google_lens.py
│       ├── output/
│       │   └── README.md
│       └── utils/
│           ├── logging_config.py
│           ├── text_utils.py
│           └── url_utils.py
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   └── endpoints/
│   │   │       ├── health.py
│   │   │       ├── auth.py
│   │   │       └── verification.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security/
│   │   │       ├── password.py
│   │   │       └── token.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── verification_session.py
│   │   ├── repositories/
│   │   │   └── verification_repository.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── verification.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       └── verification_service.py
│   └── migrations/
│       ├── env.py
│       └── versions/
│           └── 72ee75e19878_create_users_table.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── README.md
│   └── src/
│       ├── main.tsx
│       ├── app/
│       │   ├── App.tsx
│       │   └── router.tsx
│       ├── components/
│       │   ├── auth/
│       │   ├── common/
│       │   ├── layout/
│       │   └── verification/
│       ├── context/
│       │   └── AuthContext.tsx
│       ├── hooks/
│       │   └── index.ts
│       ├── pages/
│       │   ├── VerifyPage.tsx
│       │   ├── OCRReviewPage.tsx
│       │   ├── ClaimSelectionPage.tsx
│       │   ├── VerificationProgressPage.tsx
│       │   ├── ResultPage.tsx
│       │   ├── EvidencePage.tsx
│       │   ├── EvidenceDetailPage.tsx
│       │   ├── TimelinePage.tsx
│       │   ├── HistoryPage.tsx
│       │   ├── HowItWorksPage.tsx
│       │   ├── LoginPage.tsx
│       │   └── RegisterPage.tsx
│       ├── services/
│       │   ├── api.ts
│       │   └── verification.ts
│       ├── types/
│       │   └── verification.ts
│       └── utils/
│           └── verdict.ts
└── tests/ and experiment artifacts/
```

### 3.1. AI service

| File | Trách nhiệm |
|---|---|
| `ai_service/app/config.py` | Đọc cấu hình AI, đường dẫn model, timeout, OCR, số kết quả tìm kiếm, tham số BM25 và cấu hình Qwen |
| `pipeline.py` | Điều phối toàn bộ các bước phân tích |
| `input/input_processor.py` | Điều phối xử lý text/image/URL |
| `input/ocr.py` | Chuyển ảnh thành văn bản bằng Tesseract |
| `input/ocr_cleaner.py` | Loại một số thành phần giao diện, dòng nhiễu và chuẩn hóa OCR |
| `input/url_extractor.py` | Tải và trích xuất text từ URL đầu vào |
| `extraction/claim_extractor.py` | Gọi LLM để trích xuất claims và validate JSON/schema |
| `extraction/claim_schema.py` | Định nghĩa/kiểm tra cấu trúc claims |
| `extraction/json_parser.py` | Parse JSON an toàn từ output mô hình |
| `extraction/prompts/claim_extraction.txt` | Prompt trích xuất claims |
| `llm/gemini_provider.py` | Khởi tạo Gemini client và gửi generation request |
| `extraction/model_loader.py` | Load Qwen 3 8B quantization 4-bit; yêu cầu CUDA |
| `search/query_generator.py` | Chuyển claims thành search queries, gắn claim ID và loại trùng query |
| `search/google_news.py` | Tìm kiếm qua Google News RSS |
| `search/result_normalizer.py` | Chuẩn hóa metadata, deduplicate URL, lọc kết quả không hợp lệ về cấu trúc |
| `search/url_resolver.py` | Giải mã Google News RSS URL về publisher URL bằng `gnews-decoder` |
| `search/article_extractor.py` | Tải bài báo và trích xuất nội dung bằng Trafilatura hoặc BeautifulSoup fallback |
| `search/article_cleaner.py` | Loại boilerplate và paragraph trùng |
| `search/paragraph_segmenter.py` | Chia bài báo thành các đoạn có kích thước phù hợp |
| `search/bm25_retriever.py` | Xếp hạng paragraph theo BM25 cho từng claim |
| `verification/evidence_relevance.py` | Tách câu và tính độ tương đồng TF-IDF ký tự/cosine |
| `verification/verifier.py` | Load VELECTRA cục bộ và dự đoán nhãn claim-evidence |
| `verification/evidence_verification.py` | Chạy verifier trên evidence được truy xuất |
| `verification/evidence_aggregator.py` | Tổng hợp nhãn evidence thành verdict theo claim |
| `verification/verification_schema.py` | Schema nhãn và kết quả verification |
| `utils/` | Logging, chuẩn hóa text, URL và helper dùng chung |

### 3.2. Backend

| File | Trách nhiệm |
|---|---|
| `backend/app/main.py` | Tạo FastAPI app, cấu hình CORS, include router, tạo bảng metadata khi startup |
| `api/v1/router.py` | Gom health, auth và verification routers |
| `endpoints/health.py` | Health check |
| `endpoints/auth.py` | API đăng ký và đăng nhập |
| `endpoints/verification.py` | API OCR, analyze, history, get session, delete session |
| `core/config.py` | Cấu hình API prefix, JWT, frontend origin và thông tin app |
| `core/security/password.py` | Hash và verify password |
| `core/security/token.py` | Tạo access token JWT |
| `db/database.py` | Tạo SQLAlchemy engine, SessionLocal và dependency `get_db` |
| `db/base.py` | Khai báo SQLAlchemy DeclarativeBase |
| `models/user.py` | Bảng `users` |
| `models/verification_session.py` | Bảng `verification_sessions` |
| `schemas/auth.py` | Request/response schema cho auth |
| `schemas/verification.py` | Request/response schema cho verification |
| `services/auth_service.py` | Logic register/login |
| `services/verification_service.py` | Tạo session, chạy AI pipeline và cập nhật kết quả |
| `repositories/verification_repository.py` | CRUD và truy vấn lịch sử phiên |
| `migrations/env.py` | Cấu hình Alembic, đọc DATABASE_URL và metadata |

### 3.3. Frontend

| File | Trách nhiệm |
|---|---|
| `src/main.tsx` | Entry point React |
| `src/app/App.tsx` | Root application |
| `src/app/router.tsx` | Khai báo routes |
| `src/context/AuthContext.tsx` | Auth state/context |
| `src/services/api.ts` | Axios instance, base URL và token interceptor |
| `src/services/verification.ts` | Hàm gọi verification API |
| `src/types/verification.ts` | TypeScript types |
| `src/utils/verdict.ts` | Helper xử lý/hiển thị verdict |
| `src/pages/` | Các trang nhập liệu, OCR review, claims, kết quả, evidence, lịch sử, đăng nhập/đăng ký |
| `src/components/` | Component dùng chung, auth, layout và verification |

**Cấu hình frontend hiện tại:** `api.ts` đang hardcode `http://localhost:8000/api/v1`. Khi deploy cần đổi sang biến môi trường Vite, ví dụ `VITE_API_BASE_URL`.

---

## 4. Chi tiết luồng AI pipeline

Entry point chính:

```python
run_search_pipeline(
    user_input,
    input_type="text",
    max_results=GOOGLE_NEWS_MAX_RESULTS,
    top_k=BM25_TOP_K,
    selected_claims=None,
)
```

`selected_claims` có trong function signature được cung cấp nhưng chưa được sử dụng trong phần implementation đã xem. Không nên giả định tính năng chọn claim đã lọc pipeline nếu chưa cập nhật code.

### 4.1. Input processing

`process_input(user_input, input_type)` hỗ trợ:

- `text`: kiểm tra chuỗi không rỗng và lưu nội dung đã trim.
- `image`: gọi OCR, lưu extracted text và image reference.
- `url`: gọi URL extractor để lấy title, final URL và text.

Kết quả có các trường như `input_type`, `original_input`, `extracted_text`, `metadata`, `status`, `error`.

### 4.2. OCR cleaning

`clean_ocr_text()` chuẩn hóa nội dung OCR, có thể loại:
- Một số timestamp dạng giao diện mạng xã hội.
- Tên miền đứng riêng.
- Nhãn giao diện như like/comment/share/follow/subscribe.
- Các dòng “đọc thêm/xem thêm”.
- Một số ký tự hoặc đoạn quá ngắn/nhiễu.

Đây là heuristic cleaning. Nội dung ngắn nhưng quan trọng vẫn có nguy cơ bị loại, vì vậy nên kiểm tra raw OCR và cleaned OCR khi kết quả bất thường.

### 4.3. Claim extraction

`claim_extractor.py`:
1. Đọc prompt `prompts/claim_extraction.txt`.
2. Gọi `get_gemini().generate(...)`.
3. Parse output bằng `safe_json_from_model`.
4. Validate bằng `validate_claims_schema`.
5. Trả claims đã chuẩn hóa.

Code được cung cấp sử dụng Gemini qua `google-genai` và yêu cầu `GEMINI_API_KEY`. Trong `.env.example` lại có cấu hình `LLM_PROVIDER=openrouter` và `OPENROUTER_API_KEY`; đây là khác biệt cần thống nhất. Chỉ cấu hình biến môi trường không tự động làm code chuyển sang OpenRouter nếu provider implementation không đọc các biến đó.

### 4.4. Query generation

`prepare_search_queries(claims)`:
- Đọc `claim_id` hoặc tự gán ID dạng `C1`, `C2`, ...
- Chuẩn hóa `claim_text`.
- Lấy danh sách `search_queries`.
- Bỏ query rỗng và loại query trùng không phân biệt hoa/thường.
- Trả các record gồm `claim_id`, `claim_text`, `query`, `query_index`.

### 4.5. Google News search

`search_google_news()` gọi Google News RSS:

```text
https://news.google.com/rss/search?q=<query>&hl=vi&gl=VN&ceid=VN:vi
```

Các metadata được trích xuất gồm title, link, publication date, snippet và source. `search_all_queries()` chạy cho từng query, gắn `claim_id` và `search_query`, đồng thời ghi nhận lỗi theo stage.

Theo implementation đã gửi, Google News RSS không cần `SERPAPI_API_KEY`.

### 4.6. Chuẩn hóa và lọc kết quả tìm kiếm

`normalize_search_results()` chuẩn hóa title/source/date/snippet/url.

`deduplicate_results()`:
- Chuẩn hóa URL.
- Gộp kết quả có cùng URL.
- Gộp claim associations và query associations.
- Bổ sung metadata còn thiếu từ các bản ghi trùng.

`filter_search_results()` chỉ kiểm tra cấu trúc:
- URL phải là HTTP/HTTPS hợp lệ.
- Title phải có độ dài tối thiểu.

Đây **không phải** semantic relevance filtering và cũng không phải kiểm tra độ đúng/sai của bài báo.

### 4.7. Trích xuất bài báo

`resolve_google_news_urls()` giải mã URL `news.google.com` thành URL publisher bằng `gnews-decoder`.

`extract_article()`:
- Tải trang bằng Requests.
- Kiểm tra HTTP status và Content-Type.
- Đọc title, author và published date từ HTML/meta nếu có.
- Ưu tiên Trafilatura nếu đã cài.
- Nếu không trích được thì dùng BeautifulSoup, ưu tiên `article`, `main`, `body`.
- Loại script/style/nav/footer/header/aside/form/noscript khỏi fallback.
- Trả `success`, `partial` hoặc `failed` tùy lượng nội dung.

`clean_article()`:
- Loại một số boilerplate như “đọc thêm”, “xem thêm”, quảng cáo, bài viết liên quan.
- Chuẩn hóa khoảng trắng.
- Loại paragraph trùng lặp.

### 4.8. Paragraph segmentation

`segment_article()`:
- Tách nội dung theo các khối paragraph.
- Nếu chỉ có một block quá dài thì chia theo dấu kết thúc câu.
- Mặc định `min_chars=80`, `max_chars=1800`.
- Gộp các block ngắn vào block tiếp theo.
- Gán `article_id`, `paragraph_id`, `claim_ids`, title, source, URL, published date và `paragraph_text`.

### 4.9. BM25 retrieval

`bm25_retriever.py`:
- Chuẩn hóa Unicode NFC và lowercase.
- Thử dùng `underthesea.word_tokenize`; nếu không khả dụng thì dùng regex fallback.
- Thử dùng `rank_bm25.BM25Okapi`; nếu không khả dụng thì có `SimpleBM25` fallback.
- Chỉ xét paragraph gắn với claim ID tương ứng.
- Xếp hạng theo BM25 score và lấy `top_k` kết quả.

BM25 là thuật toán xếp hạng liên quan theo từ vựng, **không xác định sự thật**. BM25 score không phải xác suất claim đúng.

### 4.10. Relevance filtering

`filter_relevant_sentences()`:
- Làm sạch và tách câu từ paragraph.
- Dùng `TfidfVectorizer(analyzer="char", ngram_range=(2,4))`.
- Tính cosine similarity giữa claim và từng câu.
- Mặc định threshold trong file được cung cấp là `0.08`.
- Lưu danh sách `sentence_relevance`, `relevant_sentences` và score từng câu.

Điểm similarity phản ánh độ tương đồng từ vựng/ký tự, không chứng minh câu đó hỗ trợ hoặc phản bác claim.

### 4.11. VELECTRA verification

`verifier.py`:
- Load tokenizer và model từ `ai_service/models/velectra-vifactcheck`.
- Dùng `local_files_only=True`; model phải có sẵn trên máy.
- Chạy model trên CPU và `.eval()`.
- Tokenize claim-evidence pair, `truncation="only_second"`, `max_length=512`.
- Dùng `torch.inference_mode()` và softmax.
- Trả `label`, `confidence`, `scores`.

Label mapping trong code đã cung cấp:
- `0`: `supported`
- `1`: `refuted`
- `2`: `not_enough_information`

Đây là dự đoán của mô hình phân loại, không phải kết luận pháp lý hay bảo đảm đúng tuyệt đối.

**Điểm cần chú ý khi đọc implementation:** `evidence_relevance.py` có tính relevance ở cấp câu, nhưng `evidence_verification.py` hiện lấy `paragraph_text` và truyền toàn bộ paragraph vào `verify_pair()`. Vì vậy code hiện tại được cung cấp đang verification ở **cấp paragraph**, không phải từng `relevant_sentence`.

### 4.12. Evidence aggregation

`evidence_aggregator.py` nhận các evidence có nhãn và tổng hợp:
- `supported`
- `refuted`
- `not_enough_information`

Các verdict:
- `no_evidence`: không có evidence hợp lệ.
- `conflicting_evidence`: có cả supported và refuted.
- `supported`: chỉ có evidence supported.
- `refuted`: chỉ có evidence refuted.
- `not_enough_information`: còn evidence nhưng không đủ để kết luận supported/refuted.

File aggregator có `RELEVANCE_THRESHOLD = 0.20` và đọc các trường score ở cấp evidence như `relevance_score`, `sentence_relevance_score`, `similarity_score`, `tfidf_score`.

**Một khác biệt quan trọng trong code đã gửi:** relevance filtering lưu điểm trong cấu trúc lồng `sentence_relevance`/`relevant_sentences`, trong khi aggregator đọc các score key ở cấp evidence. Nếu không có score cấp evidence được gán ở bước khác, threshold `0.20` có thể không được áp dụng cho score câu như dự định. Cần thống nhất schema giữa hai module.

Số lượng evidence trong aggregator là số record evidence theo nhãn, không đồng nghĩa số nguồn báo chí độc lập. Các con số này cũng không phải xác suất sự thật.

---

## 5. Backend API documentation

Base prefix:

```text
/api/v1
```

Backend chạy mặc định ở `http://127.0.0.1:8000` nếu dùng lệnh chạy ở phần 8.

Swagger UI: `http://127.0.0.1:8000/docs`  
ReDoc: `http://127.0.0.1:8000/redoc`  
OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### 5.1. Health check

**GET** `/api/v1/health`

Response:

```json
{
  "status": "healthy",
  "service": "TruthCams AI Backend"
}
```

### 5.2. Register

**POST** `/api/v1/auth/register`

Request:

```json
{
  "name": "Example User",
  "email": "user@example.com",
  "password": "at-least-8-characters"
}
```

Validation:
- `name`: 2–100 ký tự.
- `email`: định dạng email hợp lệ.
- `password`: 8–128 ký tự.

Response `201 Created`:

```json
{
  "id": 1,
  "name": "Example User",
  "email": "user@example.com"
}
```

Lỗi thường gặp:
- `409 Conflict`: email đã được đăng ký.
- `422 Unprocessable Entity`: request không hợp lệ.

Service chuẩn hóa email về lowercase và trim khoảng trắng; password được hash trước khi lưu.

### 5.3. Login

**POST** `/api/v1/auth/login`

Request:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

Response:

```json
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Example User",
    "email": "user@example.com"
  }
}
```

Lỗi `401 Unauthorized` khi email/password không hợp lệ.

Frontend Axios interceptor đọc token từ localStorage key:

```text
truthcams_access_token
```

và gửi header:

```text
Authorization: Bearer <token>
```

**Phạm vi auth cần lưu ý:** Trong các endpoint verification đã xem, chưa thấy dependency xác thực user được gắn vào các route analyze/history/get/delete. `analyze_text()` cũng đang được gọi mà không truyền `user_id`. Vì vậy không nên mặc định rằng lịch sử verification đã được phân quyền theo tài khoản chỉ vì frontend có token interceptor. Cần bổ sung/kiểm tra authorization dependencies và truyền user ID đã xác thực vào service/repository.

### 5.4. OCR image

**POST** `/api/v1/verification/ocr`

Content-Type: `multipart/form-data`

Form field:

```text
file: <image file>
```

Điều kiện:
- File phải có content type dạng image.
- Kích thước tối đa 10 MB.
- PIL kiểm tra file ảnh, sau đó chuyển RGB và gọi OCR.

Response có các trường:
- `filename`
- `text`
- `raw_text`
- `character_count`
- `raw_character_count`
- `status`

Lỗi:
- `400`: file không phải ảnh hợp lệ/không đọc được.
- `413`: file vượt quá 10 MB.
- `500`: OCR thất bại.

Ví dụ cURL:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/verification/ocr" \
  -F "file=@sample.png"
```

### 5.5. Analyze text hoặc URL

**POST** `/api/v1/verification/analyze`

Request:

```json
{
  "text": "Nội dung hoặc URL cần kiểm tra"
}
```

`text` có `min_length=1`. Service tự nhận diện URL HTTP/HTTPS; nếu không phải URL thì xem là text.

Response là một verification session, gồm các trường:
- `id`
- `user_id`
- `input_type`
- `original_input`
- `status`
- `result`
- `error`
- `created_at`
- `updated_at`

Trạng thái:
- `processing`
- `success`
- `partial`
- `failed`

Ví dụ cURL:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/verification/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text":"Nội dung cần kiểm tra"}'
```

Schema `VerificationRequest` có trường `claims` tùy chọn theo source đã gửi, nhưng service hiện được xem chỉ lấy `text` và gọi pipeline. Không nên giả định trường `claims` được sử dụng.

### 5.6. Verification history

**GET** `/api/v1/verification/history`

Query parameters:
- `limit`: mặc định 20, min 1, max 100.
- `offset`: mặc định 0.

Ví dụ:

```bash
curl "http://127.0.0.1:8000/api/v1/verification/history?limit=20&offset=0"
```

Response gồm danh sách item và metadata phân trang (`items`, `total`, `limit`, `offset`).

Repository có khả năng lọc theo `user_id`, nhưng endpoint được cung cấp không truyền `user_id`. Cần sửa authorization/filtering trước khi sử dụng trong môi trường nhiều người dùng.

### 5.7. Get verification session

**GET** `/api/v1/verification/{session_id}`

Ví dụ:

```bash
curl "http://127.0.0.1:8000/api/v1/verification/1"
```

- `200`: trả session.
- `404`: không tìm thấy session.

### 5.8. Delete verification session

**DELETE** `/api/v1/verification/{session_id}`

Ví dụ:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/verification/1"
```

- `404`: không tìm thấy session.
- Response theo `DeleteResponse` schema trong backend.

### 5.9. API endpoint map

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/` | Welcome/root endpoint |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Đăng ký |
| POST | `/api/v1/auth/login` | Đăng nhập |
| POST | `/api/v1/verification/ocr` | OCR ảnh |
| POST | `/api/v1/verification/analyze` | Phân tích text/URL |
| GET | `/api/v1/verification/history` | Lịch sử |
| GET | `/api/v1/verification/{session_id}` | Chi tiết phiên |
| DELETE | `/api/v1/verification/{session_id}` | Xóa phiên |

---

## 6. Database

### 6.1. Database engine

Backend dùng SQLAlchemy và driver `psycopg` v3. Cấu hình đọc `DATABASE_URL` từ:

```text
backend/.env
```

Ví dụ PostgreSQL URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/truthcams
```

Thay `YOUR_PASSWORD` bằng password database của máy bạn. Không commit credentials lên Git.

### 6.2. Bảng users

Theo `backend/app/models/user.py` và migration đã gửi:

| Column | Type | Ý nghĩa |
|---|---|---|
| `id` | Integer, PK | ID người dùng |
| `name` | String(100) | Tên |
| `email` | String(255), unique/index | Email |
| `password_hash` | String(255) | Password hash |
| `created_at` | DateTime timezone-aware | Thời điểm tạo |

Password gốc không được lưu trực tiếp.

### 6.3. Bảng verification_sessions

Theo `backend/app/models/verification_session.py`:

| Column | Type | Ý nghĩa |
|---|---|---|
| `id` | Integer, PK | ID phiên |
| `user_id` | Integer, nullable FK | Liên kết user; on delete set null |
| `input_type` | String(20) | text/image/url |
| `original_input` | Text | Nội dung đầu vào |
| `status` | String(20) | processing/success/partial/failed |
| `result` | JSON, nullable | Kết quả pipeline |
| `error` | Text, nullable | Lỗi nếu có |
| `created_at` | DateTime timezone-aware | Thời điểm tạo |
| `updated_at` | DateTime timezone-aware | Thời điểm cập nhật |

### 6.4. Tạo database PostgreSQL

Trên Ubuntu, nếu PostgreSQL chưa được cài:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

Tạo database (cách thực hiện phụ thuộc cấu hình user PostgreSQL của máy):

```bash
sudo -u postgres psql
```

Trong prompt `psql`:

```sql
CREATE DATABASE truthcams;
\q
```

Nếu cần tạo user riêng:

```sql
CREATE USER truthcams_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE truthcams TO truthcams_user;
```

Sau đó dùng URL tương ứng trong `backend/.env`.

### 6.5. Alembic và tạo bảng

`backend/migrations/env.py`:
- Đọc `backend/.env`.
- Yêu cầu `DATABASE_URL`.
- Gán URL cho Alembic.
- Dùng `Base.metadata` làm target metadata.

Lệnh migration từ project root:

```bash
alembic -c alembic.ini upgrade head
```

Tạo migration mới sau khi cập nhật model:

```bash
alembic -c alembic.ini revision --autogenerate -m "describe_change"
```

Kiểm tra trạng thái:

```bash
alembic -c alembic.ini current
alembic -c alembic.ini history
```

**Lưu ý quan trọng:** Migration được cung cấp hiện tạo bảng `users`; chưa thấy migration tạo `verification_sessions`. Trong khi đó `main.py` gọi `Base.metadata.create_all(bind=engine)` lúc startup. Cách này có thể tạo bảng còn thiếu khi backend khởi động, nhưng schema migration sẽ không phản ánh đầy đủ nếu chưa tạo migration cho `verification_sessions`. Nên tạo và kiểm tra migration riêng cho bảng này trước khi triển khai production.

---

## 7. Cài đặt dependencies

Khuyến nghị dùng một Python virtual environment cho backend và AI pipeline vì backend import trực tiếp package `ai_service`.

### 7.1. System packages trên Ubuntu

```bash
sudo apt update
sudo apt install -y \
  python3 python3-venv python3-pip \
  build-essential \
  tesseract-ocr \
  tesseract-ocr-vie \
  tesseract-ocr-eng \
  postgresql postgresql-contrib
```

Kiểm tra Tesseract:

```bash
tesseract --version
tesseract --list-langs
```

Danh sách language cần có tối thiểu `eng` và `vie`.

### 7.2. Python virtual environment

Tại project root:

```bash
cd ~/Projects/truthcams-ai

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
```

### 7.3. Backend dependencies

File `backend/requirements.txt` được gửi có dòng cuối:

```text
python-dotenvpython-multipart
```

Dòng này bị nối sai. Hãy sửa thành hai package riêng:

```text
python-dotenv
python-multipart
```

Ngoài ra endpoint OCR import PIL, vì vậy nên thêm `Pillow` vào backend requirements nếu backend chạy trong environment không cài AI requirements.

Các package backend chính:

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  "sqlalchemy>=2.0" \
  alembic \
  pydantic-settings \
  "pwdlib[argon2]" \
  PyJWT \
  email-validator \
  "psycopg[binary]" \
  python-dotenv \
  python-multipart \
  Pillow
```

### 7.4. AI dependencies

Các package có trong `ai_service/requirements.txt`:

```bash
pip install -r ai_service/requirements.txt
```

Source đã cung cấp còn import các package cần đảm bảo có mặt nhưng không thấy trong requirements AI đã gửi:
- `google-genai`: Gemini client.
- `scikit-learn`: TF-IDF và cosine similarity.

Cài bổ sung:

```bash
pip install google-genai scikit-learn
```

Nếu checkpoint/tokenizer yêu cầu dependency bổ sung, cài theo lỗi import thực tế. Không tự cài các package CUDA/quantization nếu không dùng Qwen.

### 7.5. PyTorch và bitsandbytes

`torch` được dùng bởi VELECTRA verifier. `bitsandbytes` và `accelerate` liên quan đến Qwen 4-bit loader.

- VELECTRA code hiện được cung cấp chạy CPU.
- Qwen loader yêu cầu CUDA và sẽ báo lỗi nếu không có CUDA.
- Claim extractor hiện dùng Gemini, không phải Qwen loader.

Nếu máy không có NVIDIA CUDA tương thích, không bật `LOAD_QWEN=true` và không gọi Qwen loader. Cài PyTorch theo hướng dẫn chính thức phù hợp hệ điều hành/CUDA của máy tại trang PyTorch.

### 7.6. Frontend dependencies

Cài Node.js phiên bản tương thích với Vite 8 và package hiện tại. Kiểm tra:

```bash
node --version
npm --version
```

Cài package:

```bash
cd frontend
npm install
```

Các package chính từ `package.json` đã gửi:
- React / React DOM 19
- React Router DOM 7
- Vite 8
- TypeScript 6
- Axios
- Tailwind CSS 4 và `@tailwindcss/vite`
- lucide-react

---

## 8. Cấu hình môi trường

Dự án hiện có **hai vị trí `.env` khác nhau**:

1. `backend/.env`: database và JWT/backend settings.
2. `.env` ở project root: AI settings và LLM credentials.

Không nên mặc định một file `.env` duy nhất sẽ được cả hai phần đọc giống nhau.

### 8.1. Root `.env` cho AI

Tạo file:

```bash
cd ~/Projects/truthcams-ai
cp .env.example .env
```

Mẫu an toàn:

```env
ENVIRONMENT=development

REQUEST_TIMEOUT=25
GOOGLE_NEWS_MAX_RESULTS=10
BM25_TOP_K=5

OCR_LANGUAGE=vie+eng
OCR_CONFIG=--psm 6

QWEN_MODEL_NAME=Qwen/Qwen3-8B
LOAD_QWEN=false

SERPAPI_API_KEY=

# Claim extraction code currently calls GeminiProvider.
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
```

**Không điền API key thật vào tài liệu hoặc commit `.env`.** Thêm `.env` vào `.gitignore`.

`GEMINI_MODEL` phải là model ID còn được tài khoản/API của bạn hỗ trợ. Nếu muốn chuyển sang OpenRouter, cần kiểm tra và cập nhật provider implementation để code thật sự sử dụng `LLM_PROVIDER`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`; chỉ thêm các biến này vào `.env` là chưa đủ.

### 8.2. `backend/.env`

Tạo file:

```bash
cp backend/.env.example backend/.env
```

Nếu chưa có `backend/.env.example`, tạo thủ công:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/truthcams

JWT_SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

FRONTEND_ORIGIN=http://localhost:5173
```

Tạo secret ngẫu nhiên:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy output vào `JWT_SECRET_KEY`. Không dùng secret mẫu trong production.

### 8.3. Kiểm tra `.gitignore`

Đảm bảo không commit:
- `.env`
- `backend/.env`
- `.venv/`
- `node_modules/`
- cache Python
- file log có dữ liệu nhạy cảm
- API keys, access tokens, database passwords

Không xóa hoặc đưa model checkpoint lớn lên Git nếu repository policy không cho phép; dùng Git LFS hoặc model storage phù hợp nếu cần versioning.

---

## 9. Cách chạy dự án từ đầu

### 9.1. Checklist trước khi chạy

- [ ] PostgreSQL đã chạy.
- [ ] Database `truthcams` đã được tạo.
- [ ] `backend/.env` có `DATABASE_URL` và `JWT_SECRET_KEY`.
- [ ] Root `.env` có LLM API key phù hợp với provider trong code.
- [ ] Tesseract và language packs `vie`, `eng` đã cài.
- [ ] Python dependencies đã cài trong `.venv`.
- [ ] Checkpoint `ai_service/models/velectra-vifactcheck` tồn tại đầy đủ.
- [ ] Frontend `npm install` đã hoàn tất.

### 9.2. Terminal 1 — Backend

Tại project root:

```bash
cd ~/Projects/truthcams-ai
source .venv/bin/activate

uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Nếu import package lỗi, kiểm tra:
- Bạn đang đứng tại project root.
- Virtual environment đang active.
- Các thư mục package có `__init__.py` nếu môi trường/import layout của bạn yêu cầu.
- Các dependencies backend và AI đã cài trong cùng environment.

Backend docs:

```text
http://127.0.0.1:8000/docs
```

### 9.3. Terminal 2 — Frontend

```bash
cd ~/Projects/truthcams-ai/frontend
npm run dev
```

Vite thường hiển thị URL:

```text
http://localhost:5173
```

Mở URL mà terminal Vite thực sự in ra.

### 9.4. Build frontend

```bash
cd ~/Projects/truthcams-ai/frontend
npm run build
```

### 9.5. Lint frontend

```bash
cd ~/Projects/truthcams-ai/frontend
npm run lint
```

### 9.6. Không cần chạy AI server riêng trong kiến trúc hiện tại

Với source đã xem, backend import pipeline Python trực tiếp. Không có căn cứ để yêu cầu chạy một lệnh `uvicorn` riêng cho `ai_service`. Khi backend chạy, pipeline được gọi từ backend process.

---

## 10. Kiểm thử

### 10.1. Python tests có trong repository

Đã thấy các file test:
- `ai_service/test_ai.py`
- `ai_service/tests/test_foundation.py`
- `ai_service/tests/test_input.py`
- `ai_service/tests/test_search_modules.py`
- Root-level tests như `test_pipeline.py`, `test_pipeline_integration.py`, `test_relevance.py`, `test_verifier.py`, `test_sentence_level.py`, `test_threshold_comparison.py` và các file liên quan.

Chạy pytest từ project root:

```bash
source .venv/bin/activate
python -m pytest -q
```

Chạy một file:

```bash
python -m pytest -q ai_service/tests/test_input.py
```

Chạy test với output chi tiết:

```bash
python -m pytest -vv
```

Nếu chưa cài pytest:

```bash
pip install pytest
```

**Lưu ý:** Không phải tất cả file có tên `test_*.py` chắc chắn là pytest test tự động; một số có thể là script thực nghiệm yêu cầu API key, model hoặc dữ liệu riêng. Xem nội dung file trước khi chạy toàn bộ.

### 10.2. Kiểm tra backend

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/api/v1/health
```

### 10.3. Kiểm tra auth

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

Đăng nhập:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 10.4. Kiểm tra pipeline

Nên bắt đầu bằng một claim ngắn, rõ, có thông tin tìm kiếm được và theo dõi log của backend. Kiểm tra từng stage:
1. Input extraction.
2. Claim extraction.
3. Query generation.
4. Search results.
5. Article extraction.
6. Paragraph segmentation.
7. BM25 results.
8. Relevance filtering.
9. VELECTRA labels.
10. Aggregated verdict.

Không dùng một kết quả duy nhất làm bằng chứng rằng toàn bộ pipeline đã hoạt động đúng.

---

## 11. Lỗi thường gặp và cách xử lý

| Triệu chứng | Nguyên nhân có thể | Cách kiểm tra / xử lý |
|---|---|---|
| `ModuleNotFoundError` | Thiếu package hoặc chạy sai environment | Activate `.venv`, cài requirements, kiểm tra `which python` |
| Cài backend requirements thất bại tại `python-dotenvpython-multipart` | Hai package bị nối thành một dòng | Tách thành `python-dotenv` và `python-multipart` |
| `DATABASE_URL is not configured` | Thiếu `backend/.env` hoặc sai biến | Kiểm tra `backend/.env`, không đặt nhầm chỉ ở root `.env` |
| PostgreSQL connection refused | PostgreSQL chưa chạy hoặc sai host/port | `sudo systemctl status postgresql`, kiểm tra port và URL |
| `password authentication failed` | Sai DB username/password | Kiểm tra credentials trong `DATABASE_URL` |
| `GEMINI_API_KEY` missing | Chưa cấu hình key cho provider hiện tại | Kiểm tra root `.env` và tên biến |
| Gemini model not found / permission error | Model ID không hợp lệ hoặc API không có quyền | Kiểm tra model ID và quyền truy cập của API account |
| OCR trả text rỗng | Ảnh mờ, chữ nhỏ, ngôn ngữ thiếu hoặc Tesseract chưa cài | Kiểm tra `tesseract --list-langs`, ảnh đầu vào, raw OCR |
| `TesseractNotFoundError` | Thiếu binary Tesseract hoặc PATH | Cài `tesseract-ocr`, kiểm tra `which tesseract` |
| Không tải được bài báo | Website chặn bot, timeout, redirect hoặc URL không còn tồn tại | Kiểm tra URL, timeout, status code; thử nguồn khác |
| Article extraction chỉ có snippet | Website không cho lấy body hoặc parser không trích được | Kiểm tra `extraction_status`, `metadata_fallback`, raw HTML |
| Không có search results | RSS query không phù hợp hoặc Google News trả rỗng | Kiểm tra query được sinh, RSS response, network |
| Google News URL không resolve | Decoder lỗi hoặc thay đổi định dạng URL | Kiểm tra `url_resolver` log; publisher URL có thể không resolve được |
| Không có BM25 evidence | Không có paragraph gắn claim ID hoặc không có token overlap | Kiểm tra claim associations, paragraphs và tokenization |
| VELECTRA không load | Thiếu checkpoint/file tokenizer hoặc sai path | Kiểm tra `ai_service/models/velectra-vifactcheck` |
| Torch lỗi khi load model | Torch/dependency không tương thích | Cài PyTorch phù hợp Python/OS; xem stack trace |
| Qwen báo cần CUDA | Qwen loader được gọi trên máy không có CUDA | Giữ `LOAD_QWEN=false`; flow claim extraction hiện dùng Gemini |
| Frontend không kết nối backend | Backend chưa chạy hoặc base URL sai | Kiểm tra port 8000 và `frontend/src/services/api.ts` |
| CORS error | `FRONTEND_ORIGIN` không khớp origin frontend | Đặt đúng `http://localhost:5173` hoặc origin thực tế |
| Frontend build lỗi TypeScript | Type mismatch hoặc dependency version | Chạy `npm install`, `npm run build`, đọc lỗi cụ thể |
| History hiển thị dữ liệu không đúng user | Endpoint chưa truyền user_id filter | Bổ sung authentication dependency và filter theo current user |
| API request timeout | Pipeline đồng bộ, nhiều query/bài báo hoặc LLM chậm | Giảm số kết quả/query, tối ưu pipeline; cân nhắc background job |

### 11.1. Debug pipeline theo stage

Khi kết quả không như mong đợi, đừng chỉ xem verdict cuối cùng. Kiểm tra lần lượt:
- `claims`: model trích xuất claim đúng chưa?
- `search_queries`: query có giữ đúng ý claim không?
- `search_results`: có kết quả và URL hợp lệ không?
- `rejected_search_results`: bị loại vì lý do gì?
- `articles`: bài viết có body thật không?
- `paragraphs`: đoạn có gắn đúng claim ID không?
- `retrieved_evidence`: BM25 lấy đoạn nào?
- `filtered_evidence`: câu nào qua relevance threshold?
- `verified_evidence`: model gán nhãn nào?
- `aggregated_results`: vì sao tổng hợp ra verdict hiện tại?

---

## 12. Những điểm chưa đồng nhất / cần cải thiện

Đây là các điểm phát hiện trực tiếp từ source đã được cung cấp. Nên xử lý trước khi xem hệ thống là production-ready.

### 12.1. LLM provider configuration không khớp implementation

`.env.example` có:
- `LLM_PROVIDER=openrouter`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

Nhưng `claim_extractor.py` đang gọi `get_gemini()` và `gemini_provider.py` yêu cầu `GEMINI_API_KEY`.

**Cần làm:** Chọn một provider làm chuẩn. Nếu chọn Gemini, cập nhật `.env.example` theo Gemini và bỏ biến OpenRouter không dùng. Nếu chọn OpenRouter, viết provider tương ứng và cập nhật claim extractor/config để gọi provider đó.

### 12.2. API key đã xuất hiện trong terminal/chat

Một giá trị có định dạng OpenRouter key đã được dán trong nội dung `.env.example` gửi lên hội thoại.

**Cần làm ngay:**
1. Revoke/rotate key cũ trên OpenRouter.
2. Tạo key mới.
3. Chỉ lưu key mới trong `.env` local.
4. Đảm bảo `.env` nằm trong `.gitignore`.
5. Không đưa key vào README, source code, ảnh chụp terminal hoặc tài liệu chia sẻ.

### 12.3. Backend requirements bị nối package

Sửa:

```text
python-dotenvpython-multipart
```

thành:

```text
python-dotenv
python-multipart
```

Thêm Pillow nếu backend environment cần chạy OCR endpoint độc lập.

### 12.4. Thiếu dependencies trong AI requirements

Code đã cung cấp import:
- `google.genai` → package `google-genai`.
- `sklearn` → package `scikit-learn`.

Đảm bảo requirements phản ánh dependencies thực tế để người khác có thể cài lại môi trường từ đầu.

### 12.5. Verification README cũ

`ai_service/app/verification/README.md` ghi notebook hiện dừng ở BM25 và chưa implement VELECTRA/aggregation. Tuy nhiên source hiện có `verifier.py`, `evidence_verification.py`, `evidence_aggregator.py`.

**Cần làm:** Cập nhật README theo implementation hiện tại, đồng thời mô tả chính xác giới hạn của nó.

### 12.6. Sentence relevance nhưng paragraph verification

`evidence_relevance.py` tính relevance từng câu, nhưng `evidence_verification.py` dùng `paragraph_text` để gọi verifier.

**Cần quyết định một thiết kế thống nhất:**
- Option A: verification từng câu đã qua relevance filtering.
- Option B: verification toàn paragraph và đặt tên/metadata cho đúng cấp paragraph.

Nếu chọn Option A, cần lưu sentence text, sentence ID, paragraph context và source metadata để truy vết.

### 12.7. Aggregator threshold chưa khớp schema relevance

Relevance filter lưu score lồng trong `sentence_relevance`, trong khi aggregator đọc score cấp evidence. Có khả năng threshold aggregator không nhìn thấy score câu.

**Cần làm:** Thống nhất một schema evidence; ví dụ thêm `relevance_score` ở cấp evidence nếu evidence là sentence, hoặc aggregator phải đọc đúng trường nested nếu evidence là paragraph chứa nhiều câu.

### 12.8. Authorization và dữ liệu lịch sử

Auth register/login đã có; Axios interceptor đính kèm Bearer token. Tuy nhiên verification endpoints được xem chưa có dependency xác thực và chưa truyền user ID vào analyze/history/delete.

**Cần làm:**
- Xác thực token tại các route cần bảo vệ.
- Lấy user ID từ token đã xác minh, không tin user ID từ client.
- Lưu `user_id` khi tạo session.
- Lọc history/get/delete theo user hiện tại.
- Trả 404 hoặc 403 phù hợp khi session không thuộc user.

### 12.9. Alembic migration thiếu verification_sessions

Migration được cung cấp chỉ tạo `users`. Model `VerificationSession` tồn tại, và `create_all()` trong startup có thể tạo bảng, nhưng migration history chưa phản ánh bảng đó.

**Cần làm:** Đảm bảo Alembic metadata import đầy đủ cả `User` và `VerificationSession`, sau đó autogenerate và review migration tạo `verification_sessions`.

### 12.10. Frontend API URL hardcode

`frontend/src/services/api.ts` đang hardcode `http://localhost:8000/api/v1`.

**Cần làm:** Chuyển sang `import.meta.env.VITE_API_BASE_URL` và tạo `.env.development`/`.env.production` tương ứng.

### 12.11. Claim selection chưa được xác nhận hoạt động end-to-end

`selected_claims` có trong pipeline signature, `VerificationRequest` có thể có trường `claims`, nhưng code service/pipeline đã xem chưa sử dụng chúng để giới hạn phân tích.

**Cần làm:** Nếu UI cho phép chọn claims, cần nối selection từ frontend → API schema → service → pipeline, hoặc bỏ UI/field nếu chưa implement.

### 12.12. Đồng bộ request có thể gây thời gian chờ dài

Pipeline gồm LLM, RSS search, tải nhiều URL và inference. Vì được gọi đồng bộ trong request, thời gian phản hồi có thể dài.

**Hướng cải thiện:** Chuyển phân tích sang background task/queue, lưu trạng thái session, cung cấp endpoint polling hoặc WebSocket/SSE. Đây là hướng phát triển, không phải mô tả implementation hiện tại.

---

## 13. Giới hạn khi diễn giải kết quả

1. **LLM claim extraction:** có thể bỏ sót, gộp hoặc diễn đạt lại claim không chính xác.
2. **Google News RSS:** không đại diện toàn bộ nguồn tin trên Internet; kết quả phụ thuộc query, thời điểm và khả năng truy cập.
3. **Article extraction:** website có thể chặn crawler, thay đổi HTML hoặc chỉ cho lấy một phần nội dung.
4. **BM25:** đo độ liên quan từ vựng, không đo tính đúng sai.
5. **TF-IDF/cosine:** đo độ tương đồng ký tự/từ ngữ, không xác minh sự thật.
6. **VELECTRA:** dự đoán theo dữ liệu huấn luyện và label mapping của checkpoint; có thể sai với chủ đề, ngôn ngữ, ngữ cảnh hoặc cách diễn đạt ngoài phân phối.
7. **Evidence aggregation:** verdict phụ thuộc evidence được truy xuất và nhãn model; conflicting evidence không tự động có nghĩa hai nguồn có độ tin cậy ngang nhau.
8. **Source quality:** số lượng evidence không thay thế đánh giá độ tin cậy, tính độc lập và thời điểm của nguồn.
9. **OCR:** lỗi nhận dạng ký tự có thể làm thay đổi nội dung claim.
10. **URL extraction:** nội dung trang web có thể cập nhật hoặc biến mất, nên kết quả cần lưu metadata nguồn và thời điểm truy xuất.

TruthCams AI nên được xem là công cụ hỗ trợ khảo sát evidence, không phải hệ thống tự động đưa ra kết luận pháp lý hoặc xác nhận sự thật tuyệt đối.

---

## 14. Bảo mật và triển khai

Trước khi deploy:
- Rotate API key đã bị lộ.
- Không commit `.env`.
- Dùng HTTPS.
- Dùng JWT secret mạnh, riêng cho từng môi trường.
- Bổ sung authorization cho verification routes.
- Giới hạn request size và rate limit.
- Kiểm tra URL đầu vào để giảm rủi ro SSRF (chặn localhost/private IP và các scheme không hợp lệ nếu phù hợp use case).
- Đặt timeout cho outbound HTTP.
- Không log password, token, API key hoặc dữ liệu cá nhân không cần thiết.
- Kiểm tra quyền truy cập file upload và giới hạn kích thước.
- Không bật `--reload` trong production.
- Dùng process manager/container orchestration phù hợp.
- Tách background processing nếu pipeline dài.
- Tạo migration đầy đủ và backup database.
- Thiết lập monitoring/logging và xử lý lỗi tập trung.

---

## 15. Quick start — bản rút gọn

Sau khi đã cài dependencies, PostgreSQL và cấu hình hai file `.env`:

**Terminal 1 — Backend**

```bash
cd ~/Projects/truthcams-ai
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend**

```bash
cd ~/Projects/truthcams-ai/frontend
npm run dev
```

Mở frontend URL Vite in ra, thường là:

```text
http://localhost:5173
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

---

## 16. Thông tin cần xác minh khi cập nhật source

Tài liệu này có thể cần cập nhật nếu thay đổi:
- Provider LLM (Gemini/OpenRouter).
- Claim schema và prompt.
- Label mapping hoặc checkpoint VELECTRA.
- Relevance threshold và schema score.
- Sentence-level hay paragraph-level verification.
- API authentication/authorization.
- Database migration.
- Frontend API base URL.
- Số lượng kết quả search, `top_k`, timeout.
- Cách chạy pipeline (đồng bộ hay background).

Khi sửa source, nên cập nhật đồng thời:
1. Code implementation.
2. Unit/integration tests.
3. README/module documentation.
4. File `.env.example` (chỉ chứa placeholder).
5. `SOURCE_CODE_GUIDE.md`.

---

**End of guide.**

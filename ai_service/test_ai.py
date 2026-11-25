
import sys
import tempfile
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT IMPORT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_service.app.pipeline import run_search_pipeline
from ai_service.app.config import (
    GOOGLE_NEWS_MAX_RESULTS,
    BM25_TOP_K,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Truthcams AI | Pipeline Testing",
    page_icon="🛡️",
    layout="wide",
)


# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0;
        }

        .sub-title {
            color: #888;
            margin-top: 0.2rem;
        }

        div.stButton > button {
            width: 100%;
            min-height: 45px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div>
        <div class="main-title">🛡️ Truthcams AI</div>
        <div class="sub-title">
            AI Pipeline Testing Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================

with st.sidebar:
    st.header("Pipeline Configuration")

    max_results = st.number_input(
        "Maximum search results",
        min_value=1,
        max_value=30,
        value=int(GOOGLE_NEWS_MAX_RESULTS),
        step=1,
    )

    top_k = st.number_input(
        "BM25 Top-K",
        min_value=1,
        max_value=20,
        value=int(BM25_TOP_K),
        step=1,
    )

    st.divider()

    st.caption(
        "This dashboard runs the actual Python AI pipeline. "
        "It does not simulate model or retrieval results."
    )


# =========================================================
# INPUT SECTION
# =========================================================

st.header("1. Input Information")

input_type = st.radio(
    "Choose input type",
    options=["Text", "Image"],
    horizontal=True,
)

user_text = ""
uploaded_image = None

if input_type == "Text":

    user_text = st.text_area(
        "Enter information to analyze",
        height=220,
        placeholder=(
            "Paste a Facebook post, news excerpt, "
            "or suspicious information here..."
        ),
    )

else:

    uploaded_image = st.file_uploader(
        "Upload an image containing text",
        type=["png", "jpg", "jpeg", "webp", "bmp"],
    )

    if uploaded_image is not None:
        st.image(
            uploaded_image,
            caption="Uploaded image",
            use_container_width=True,
        )


# =========================================================
# RUN PIPELINE
# =========================================================

st.write("")

run_button = st.button(
    "Run AI Pipeline",
    type="primary",
    use_container_width=True,
)

if run_button:

    if input_type == "Text" and not user_text.strip():
        st.warning("Please enter some text first.")

    elif input_type == "Image" and uploaded_image is None:
        st.warning("Please upload an image first.")

    else:

        pipeline_input = None
        temporary_path = None

        try:

            if input_type == "Text":
                pipeline_input = user_text.strip()
                pipeline_input_type = "text"

            else:
                suffix = Path(uploaded_image.name).suffix.lower()

                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False,
                ) as temp_file:

                    temp_file.write(uploaded_image.getvalue())
                    temporary_path = Path(temp_file.name)

                pipeline_input = str(temporary_path)
                pipeline_input_type = "image"

            with st.spinner(
                "Running Truthcams AI pipeline. "
                "This may take some time..."
            ):

                result = run_search_pipeline(
                    user_input=pipeline_input,
                    input_type=pipeline_input_type,
                    max_results=int(max_results),
                    top_k=int(top_k),
                )

            st.session_state["pipeline_result"] = result
            st.session_state["pipeline_input_type"] = pipeline_input_type

        except Exception as exc:

            st.error(
                f"Pipeline execution error: "
                f"{type(exc).__name__}: {exc}"
            )

            st.session_state.pop("pipeline_result", None)

        finally:

            if temporary_path and temporary_path.exists():
                temporary_path.unlink()


# =========================================================
# RESULT DASHBOARD
# =========================================================

if "pipeline_result" in st.session_state:

    result = st.session_state["pipeline_result"]

    st.divider()
    st.header("2. Pipeline Results")

    status = result.get("pipeline_status", "unknown")

    if status == "success":
        st.success("Pipeline completed successfully.")

    elif status == "partial":
        st.warning(
            "Pipeline completed partially. "
            "Some stages may have errors or incomplete results."
        )

    else:
        st.error("Pipeline failed. Check the error details below.")

    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------

    claims = result.get("claims", [])
    queries = result.get("search_queries", [])
    search_results = result.get("search_results", [])
    articles = result.get("articles", [])
    paragraphs = result.get("paragraphs", [])
    evidence = result.get("retrieved_evidence", [])
    errors = result.get("errors", [])

    col1, col2, col3 = st.columns(3)

    col1.metric("Claims", len(claims))
    col2.metric("Search Results", len(search_results))
    col3.metric("Retrieved Evidence", len(evidence))

    col4, col5, col6 = st.columns(3)

    col4.metric("Search Queries", len(queries))
    col5.metric("Articles", len(articles))
    col6.metric("Paragraphs", len(paragraphs))

    # -----------------------------------------------------
    # INPUT PROCESSING
    # -----------------------------------------------------

    with st.expander("1. Input Processing", expanded=True):

        input_data = result.get("input", {})

        metadata = input_data.get("metadata", {})

        st.write("**Input type:**", input_data.get("input_type"))
        st.write("**Status:**", metadata.get("status"))
        st.write("**Error:**", metadata.get("error") or "None")

        extracted_text = input_data.get("extracted_text", "")

        st.text_area(
            "Extracted text",
            value=extracted_text,
            height=180,
            disabled=True,
            key="extracted_text_result",
        )

    # -----------------------------------------------------
    # CLAIM EXTRACTION
    # -----------------------------------------------------

    with st.expander("2. Claim Extraction", expanded=True):

        if claims:
            for index, claim in enumerate(claims, start=1):

                st.markdown(f"**Claim {index}**")
                st.json(claim)

                if index < len(claims):
                    st.divider()

        else:
            st.info("No claims were extracted.")

    # -----------------------------------------------------
    # SEARCH QUERIES
    # -----------------------------------------------------

    with st.expander("3. Search Queries"):

        if queries:
            for index, query in enumerate(queries, start=1):
                st.write(f"{index}. {query}")
        else:
            st.info("No search queries generated.")

    # -----------------------------------------------------
    # GOOGLE NEWS RESULTS
    # -----------------------------------------------------

    with st.expander("4. Google News Search Results"):

        if search_results:
            for index, item in enumerate(search_results, start=1):

                st.markdown(f"**Result {index}**")

                title = item.get("title", "No title")
                url = item.get("url")

                st.write(title)

                if url:
                    st.markdown(f"[Open source]({url})")

                st.json(item)

                st.divider()

        else:
            st.info("No search results found.")

    # -----------------------------------------------------
    # ARTICLE EXTRACTION
    # -----------------------------------------------------

    with st.expander("5. Extracted Articles"):

        if articles:
            for index, article in enumerate(articles, start=1):

                title = article.get("title", f"Article {index}")

                with st.expander(title):

                    st.write(
                        "**Extraction status:**",
                        article.get("extraction_status"),
                    )

                    st.write(
                        "**Publisher URL:**",
                        article.get("publisher_url"),
                    )

                    st.write(
                        article.get("text", article.get("content", ""))
                    )

                    st.json(article)

        else:
            st.info("No articles extracted.")

    # -----------------------------------------------------
    # PARAGRAPHS
    # -----------------------------------------------------

    with st.expander("6. Segmented Paragraphs"):

        if paragraphs:
            for index, paragraph in enumerate(paragraphs, start=1):

                st.markdown(f"**Paragraph {index}**")

                if isinstance(paragraph, dict):
                    st.write(
                        paragraph.get(
                            "text",
                            paragraph.get("content", str(paragraph)),
                        )
                    )
                else:
                    st.write(paragraph)

        else:
            st.info("No paragraphs generated.")

    # -----------------------------------------------------
    # BM25 EVIDENCE
    # -----------------------------------------------------

    with st.expander("7. BM25 Retrieved Evidence", expanded=True):

        if evidence:
            for index, item in enumerate(evidence, start=1):

                st.markdown(f"**Evidence group {index}**")

                st.json(item)

                st.divider()

        else:
            st.warning("No evidence retrieved.")

    # -----------------------------------------------------
    # ERRORS
    # -----------------------------------------------------

    with st.expander(
        f"8. Pipeline Errors ({len(errors)})",
        expanded=bool(errors),
    ):

        if errors:
            for index, error in enumerate(errors, start=1):

                st.markdown(f"**Error {index}**")

                st.json(error)

        else:
            st.success("No pipeline errors recorded.")

    # -----------------------------------------------------
    # EXPORT RAW RESULT
    # -----------------------------------------------------

    st.divider()

    import json

    st.download_button(
        label="Download Full Pipeline Result (JSON)",
        data=json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        file_name="truthcams_pipeline_result.json",
        mime="application/json",
    )

    st.caption(
        "Note: BM25 evidence represents retrieved evidence candidates. "
        "This pipeline does not yet classify information as true or false."
    )

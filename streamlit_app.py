#!/usr/bin/env python3
"""Streamlit web UI for the Audio Transcription & Documentation Tool."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import uuid
import zipfile
from pathlib import Path
from typing import Iterable

import streamlit as st
from openai import OpenAI

import main as transcriber


st.set_page_config(
    page_title="Audio to Word Transcript",
    page_icon="🎙️",
    layout="centered",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 19px;
    }

    .stApp {
        font-size: 1.08rem;
    }

    h1 {
        font-size: 3rem !important;
        line-height: 1.12 !important;
    }

    h2, [data-testid="stHeader"] h2 {
        font-size: 2.25rem !important;
    }

    h3 {
        font-size: 1.65rem !important;
    }

    p, li, label, div[data-testid="stMarkdownContainer"],
    div[data-testid="stText"], div[data-testid="stAlert"] {
        font-size: 1.08rem !important;
        line-height: 1.65 !important;
    }

    .stButton button, .stDownloadButton button,
    div[data-testid="stFileUploader"] button {
        font-size: 1.05rem !important;
        padding: 0.65rem 1rem !important;
    }

    div[data-testid="stExpander"] summary {
        font-size: 1.12rem !important;
        line-height: 1.45 !important;
    }

    div[data-testid="stCaptionContainer"] {
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SUPPORTED_FORMATS = tuple(ext.lstrip(".") for ext in transcriber.SUPPORTED_FORMATS)
BASE_DIR = Path(__file__).parent.resolve()
INPUT_DIR = BASE_DIR / transcriber.INPUT_DIR
OUTPUT_DIR = BASE_DIR / transcriber.OUTPUT_DIR
COMPRESSED_DIR = BASE_DIR / transcriber.COMPRESSED_DIR
LESSONS_PATH = BASE_DIR / "data" / "shaykha_lessons.json"


@st.cache_data(show_spinner=False)
def load_shaykha_lessons() -> list[dict]:
    """Load the sample interpretive lesson library mined from existing transcript DOCX files."""
    if not LESSONS_PATH.exists():
        return []
    return json.loads(LESSONS_PATH.read_text(encoding="utf-8"))


def safe_filename(filename: str) -> str:
    """Keep uploaded filenames filesystem-safe while preserving readable dates/titles."""
    name = Path(filename).name
    stem = Path(name).stem
    suffix = Path(name).suffix.lower()
    cleaned_stem = re.sub(r"[^A-Za-z0-9._()\- ,]+", "_", stem).strip(" ._")
    return f"{cleaned_stem or 'audio'}{suffix}"


def ensure_dirs() -> None:
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    COMPRESSED_DIR.mkdir(exist_ok=True)


def get_secret_api_key() -> str | None:
    """Return an OpenAI key from Streamlit secrets or environment, if configured."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.getenv("OPENAI_API_KEY")


def configure_openai_client(api_key: str | None) -> None:
    """Refresh the module-level OpenAI client after a key is entered in the UI."""
    resolved_key = api_key or get_secret_api_key()
    if resolved_key:
        os.environ["OPENAI_API_KEY"] = resolved_key
    transcriber.client = OpenAI(
        api_key=resolved_key,
        timeout=transcriber.timeout_config,
        max_retries=0,
    )


def process_uploaded_files(uploaded_files: Iterable, keep_compressed: bool) -> list[dict]:
    ensure_dirs()
    results: list[dict] = []

    for uploaded_file in uploaded_files:
        filename = safe_filename(uploaded_file.name)
        download_name = f"{Path(filename).stem}.docx"
        # Prefix with a short run ID so hosted users do not collide when two people
        # upload files with the same name. Download labels keep the original name.
        run_prefix = uuid.uuid4().hex[:8]
        input_path = INPUT_DIR / f"{run_prefix}-{filename}"
        output_path = OUTPUT_DIR / f"{input_path.stem}.docx"

        input_path.write_bytes(uploaded_file.getbuffer())

        log_buffer = io.StringIO()
        with contextlib.redirect_stdout(log_buffer):
            success = transcriber.process_audio_file(input_path, keep_compressed=keep_compressed)

        results.append(
            {
                "name": filename,
                "download_name": download_name,
                "success": success,
                "output_path": output_path if output_path.exists() else None,
                "log": log_buffer.getvalue(),
            }
        )

    return results


def create_results_zip(results: list[dict]) -> bytes | None:
    """Create an in-memory ZIP containing all successfully generated .docx files."""
    successful_results = [r for r in results if r.get("success") and r.get("output_path")]
    if not successful_results:
        return None

    zip_buffer = io.BytesIO()
    used_names: set[str] = set()
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for result in successful_results:
            docx_path = Path(result["output_path"])
            archive_name = result.get("download_name") or docx_path.name
            if archive_name in used_names:
                archive_name = f"{docx_path.stem}.docx"
            used_names.add(archive_name)
            zip_file.writestr(archive_name, docx_path.read_bytes())

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


st.title("🎙️ Audio to Word Transcript")
st.caption("Upload audio, transcribe with OpenAI Whisper, format it, and download a .docx transcript.")

with st.expander("How outputs are named", expanded=False):
    st.write(
        "Each output is a Word document in the `output/` folder using the uploaded audio filename. "
        "For example, `Juma Khutba with Shaykha Fariha - Mar 31, 2023.mp3` becomes "
        "`Juma Khutba with Shaykha Fariha - Mar 31, 2023.docx`."
    )

api_key_from_secret = bool(get_secret_api_key())
if api_key_from_secret:
    st.info("OpenAI API key is configured on the server. Your friend does not need to paste one.")

api_key = st.text_input(
    "OpenAI API key",
    type="password",
    placeholder="sk-...",
    help="Optional if OPENAI_API_KEY is configured as a hosting secret; otherwise paste a key here.",
)

keep_compressed = st.checkbox(
    "Keep compressed MP3 files after processing",
    value=False,
    help="Useful for debugging; otherwise compressed temporary files are deleted.",
)

uploaded_files = st.file_uploader(
    "Upload one or more audio files",
    type=SUPPORTED_FORMATS,
    accept_multiple_files=True,
)

if uploaded_files:
    st.caption(f"Batch ready: {len(uploaded_files)} file(s) selected. They will be processed one at a time.")

if st.button("Create Word transcript", type="primary", disabled=not uploaded_files):
    if not api_key and not api_key_from_secret:
        st.error("Add an OpenAI API key first, or configure OPENAI_API_KEY as a hosting secret.")
        st.stop()

    configure_openai_client(api_key or None)

    with st.spinner("Processing audio. Long files can take several minutes..."):
        results = process_uploaded_files(uploaded_files, keep_compressed=keep_compressed)

    successful_count = sum(1 for r in results if r.get("success") and r.get("output_path"))
    st.write(f"Batch complete: {successful_count}/{len(results)} file(s) created successfully.")

    zip_bytes = create_results_zip(results)
    if zip_bytes and successful_count > 1:
        st.download_button(
            "Download all .docx files as ZIP",
            data=zip_bytes,
            file_name="transcripts.zip",
            mime="application/zip",
            key="download-all-transcripts",
        )

    for result in results:
        st.subheader(result["name"])
        if result["success"] and result["output_path"]:
            st.success("Done — Word document created.")
            docx_path = Path(result["output_path"])
            st.download_button(
                "Download .docx",
                data=docx_path.read_bytes(),
                file_name=result.get("download_name") or docx_path.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"download-{docx_path.name}",
            )
        else:
            st.error("Processing failed. See log below.")

        with st.expander("Processing log"):
            st.code(result["log"] or "No output captured.")

st.divider()
st.header("📚 Shaykha Golden Insights sample")
st.caption(
    "A sample of what this transcript archive can become after extraction: source-grounded "
    "interpretive lessons with the transcript passage, interpretation, golden insight, and practice."
)

lessons = load_shaykha_lessons()
if lessons:
    themes = sorted({lesson["theme"] for lesson in lessons})
    selected_theme = st.selectbox(
        "Filter lessons by theme",
        ["All themes", *themes],
        key="shaykha-theme-filter",
    )
    filtered_lessons = [
        lesson for lesson in lessons
        if selected_theme == "All themes" or lesson["theme"] == selected_theme
    ]
    st.write(f"Showing {len(filtered_lessons)} of {len(lessons)} sample lessons mined from the DOCX transcript archive.")

    for lesson in filtered_lessons:
        with st.expander(f"{lesson['id']:02d}. {lesson['title']}", expanded=False):
            st.caption(f"{lesson['theme']} • {lesson['sourceDate']} • {lesson['sourceTitle']}")
            st.markdown("**Transcript passage**")
            st.info(f"“{lesson['passage']}”")
            st.markdown("**Interpretation**")
            st.write(lesson["interpretation"])
            st.markdown("**Golden insight**")
            st.success(lesson["goldenInsight"])
            st.markdown("**Practice**")
            st.write(lesson["practice"])
else:
    st.warning("No sample lesson data found. Expected `data/shaykha_lessons.json`.")

st.divider()
st.markdown(
    "**Run locally:** `streamlit run streamlit_app.py`  \n"
    "**Note:** this app runs the transcription on the machine where Streamlit is running."
)

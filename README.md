# Audio Transcription & Documentation Tool

A Python CLI tool that processes audio files by compressing them, transcribing with OpenAI Whisper, formatting with GPT-5-mini, and saving as Word documents (.docx).

## Features

- Automatic audio compression using FFmpeg (64kbps MP3, 16kHz, mono)
- Transcription using OpenAI Whisper API (automatically uses latest Whisper model)
- Intelligent formatting with GPT-5-mini (title, summary, and structured transcript)
- Professional Word document output with proper formatting
- Batch processing of multiple audio files
- Comprehensive error handling and progress tracking
- Optional compressed file retention

## Prerequisites

1. **Python 3.7+**
2. **FFmpeg** - Must be installed on your system
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
3. **OpenAI API Key** - Get one from [platform.openai.com](https://platform.openai.com/api-keys)

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
# Option 1: Using .env file (recommended)
cp .env.example .env
# Edit .env and add your API key

# Option 2: Export as environment variable
export OPENAI_API_KEY='your-key-here'
```

## Project Structure

```
transcription/
├── input/          # Place audio files here
├── compressed/     # Compressed audio (temporary)
├── output/         # Final .docx files
├── main.py         # Main script
├── requirements.txt
├── .env.example
└── README.md
```

## Usage

### Basic Usage

1. Place audio files in the `input/` folder
2. Run the script:
```bash
python main.py
```
3. Find your Word documents in the `output/` folder

### Web App Usage

For a shareable local browser interface, run:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the Streamlit URL in your browser, upload one or more audio files, and download the generated `.docx` files. The web app uses the same pipeline as `main.py`: uploaded files are saved into `input/`, compressed files are created in `compressed/`, and final Word documents are saved in `output/`.

Your friend will need:

- Python 3.7+
- FFmpeg installed (`brew install ffmpeg` on macOS)
- An OpenAI API key entered in the web app or saved in `.env` as `OPENAI_API_KEY=...`

### Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)
- AAC (.aac)

### Command Line Options

```bash
# Keep compressed audio files after processing
python main.py --keep-compressed
```

By default, compressed audio files are deleted after processing. Use `--keep-compressed` to retain them in the `compressed/` folder.

## Output Format

Each processed audio file generates a Word document (.docx) with the following structure:

```
[Generated Title] (Heading 1, Bold)

Summary (Heading 2)
[2-3 sentence summary] (Normal text)

Transcript (Heading 2)
[Formatted transcript with logical paragraph breaks] (Normal text)
```

## How It Works

1. **Compression**: Audio files are compressed to 64kbps MP3 format (16kHz, mono) to reduce file size
2. **Size Check**: Ensures compressed file is under 25MB (Whisper API limit)
3. **Transcription**: Uses OpenAI Whisper API to generate text transcript
4. **Formatting**: GPT-5-mini analyzes the transcript and creates:
   - A descriptive title (5-10 words)
   - A concise summary (2-3 sentences)
   - A well-formatted transcript with logical paragraphs
5. **Document Creation**: Generates a professional Word document with proper styling

## Error Handling

The tool handles various error scenarios:

- Missing or invalid API key
- FFmpeg compression failures
- Files exceeding 25MB after compression
- Transcription API errors
- GPT-5-mini formatting errors
- Document creation failures

If a file fails, the script continues processing remaining files and provides a summary at the end.

## File Size Limits

- The OpenAI Whisper API has a 25MB file size limit
- Audio files are compressed to 64kbps to minimize size
- Files that exceed 25MB after compression will be skipped with an error message

## Example Output

```
============================================================
Audio Transcription & Documentation Tool
============================================================

Found 3 audio file(s) to process

Processing: interview.mp3
  Compressing audio...
  Compressed file size: 8.45MB
  Transcribing audio...
  Formatting with GPT-5...
  Creating Word document...
  SUCCESS: Created interview.docx

Processing: meeting.wav
  Compressing audio...
  Compressed file size: 12.32MB
  Transcribing audio...
  Formatting with GPT-5...
  Creating Word document...
  SUCCESS: Created meeting.docx

============================================================
PROCESSING COMPLETE
============================================================
Successful: 2
Failed: 0
Total: 2

Output documents saved to: output/
```

## Cost Considerations

This tool uses OpenAI's paid APIs:

- **Whisper API**: $0.006 per minute of audio
- **GPT-5-mini API**: $0.25 per 1M input tokens, $2 per 1M output tokens (typically less than a cent per transcript)

Monitor your usage at [platform.openai.com/usage](https://platform.openai.com/usage)

## Troubleshooting

### FFmpeg not found
```
ERROR: FFmpeg not installed or not in PATH
```
Solution: Install FFmpeg (see Prerequisites)

### API key not set
```
ERROR: OPENAI_API_KEY not found in environment variables
```
Solution: Create a `.env` file or export the environment variable

### File too large
```
ERROR: File still too large after compression (28.5MB > 25MB)
```
Solution: The audio file is too long. Consider splitting it into smaller segments.

### Import errors
```
ModuleNotFoundError: No module named 'openai'
```
Solution: Install dependencies with `pip install -r requirements.txt`

## License

This project is provided as-is for personal and commercial use.

## Contributing

Feel free to submit issues or pull requests to improve the tool.

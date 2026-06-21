# Hosted Web App Deployment

This app is intended to be hosted as a simple Streamlit web app so someone can open a URL, upload audio, and download a formatted `.docx` transcript.

## Recommended: Streamlit Community Cloud

Best fit for sharing with one friend because it is the fastest path from this folder to a public URL.

### 1. Put this folder in a GitHub repo

Create a repo containing at least:

- `streamlit_app.py`
- `main.py`
- `requirements.txt`
- `packages.txt`
- `.streamlit/config.toml`
- `README.md`
- `DEPLOYMENT.md`
- `.gitignore`

Do **not** commit `.env`, `input/`, `compressed/`, `output/`, or existing transcript/audio files.

### 2. Deploy on Streamlit Cloud

1. Go to <https://share.streamlit.io/>
2. Create a new app from the GitHub repo
3. Main file path: `streamlit_app.py`
4. Deploy

`packages.txt` installs FFmpeg on the hosted machine.

### 3. Configure OpenAI key

In Streamlit Cloud app settings, add this secret:

```toml
OPENAI_API_KEY = "sk-..."
```

If you configure the secret, your friend can use the app without seeing or pasting the API key. Usage will bill to that key.

Alternative: leave the secret unset and have the app ask your friend to paste his own key.

## Good paid alternative: Render

Render is better if Streamlit Cloud times out on long files or you want a more durable server.

Use these settings:

- Environment: Python
- Build command: `pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg` if supported by your plan/environment, or use a Dockerfile
- Start command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
- Environment variable: `OPENAI_API_KEY=sk-...`

## Not recommended: Cloudflare Workers

Cloudflare Workers are not a good fit for this version because the app needs:

- FFmpeg compression
- long-running OpenAI upload/transcription requests
- server-side `.docx` generation
- file upload/download handling

You could build a Cloudflare architecture later with R2 + Queues + a separate worker/container service, but that is overkill for sharing with one friend.

## Important operational notes

- Hosted files are temporary. The app lets users download the `.docx`; do not rely on the server as permanent storage.
- Large audio files can take several minutes.
- OpenAI Whisper has a compressed file size limit; this app compresses first, then rejects files that are still too large.
- If multiple people use it simultaneously, output files get a short random prefix to prevent filename collisions.

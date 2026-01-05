# Kivy client (Delphia Fitness)

Run requirements (recommended in a virtualenv):

```bash
python -m pip install -r apps/delphia/kivy/requirements.txt
```

Run the app locally (recommended):

```bash
python apps/delphia/kivy/main.py
```

Notes:
- The Kivy client no longer uses local JsonStore for persistence; it will attempt to POST profile data to the backend at `DELPHIA_BACKEND_URL` (env var) or `http://localhost:8000` by default. If the backend cannot be contacted, it will fall back to a local `profile.json` file in the working directory.
- CI: a workflow is included to validate that the KV file parses correctly (this requires installing `kivy`/`kivymd` in CI).
- If you want headless smoke tests (Xvfb), we can add that to CI next.

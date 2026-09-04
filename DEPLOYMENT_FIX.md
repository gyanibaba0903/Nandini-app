Cloudflare Python Worker deployment fix.

Cloudflare currently requires python_workers and Pywrangler to bundle Python dependencies.
This first deployment test removes python-dotenv and Groq imports so the Worker can prove
that Flask + the Cloudflare Python runtime are working. The LLM connection is added after
this deployment succeeds.

Cloudflare Workers Builds settings:
Build command: leave empty
Deploy command: pipx run --spec workers-py pywrangler deploy

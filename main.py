import os

from fastapi_poe import make_app
from modal import App, Image, Secret, asgi_app

from akkadian_talker_bot import AkkadianTalkerBot, BOT

# Specific to hosting with modal.com.
# Set these at deploy time so each bot points at its own secret and Poe-side name, e.g.:
#   POE_SECRET_NAME=akkadian-talker-oracle-secret POE_BOT_NAME=AkkadianOracle modal deploy main.py
#   BOT_MODEL=GPT-5 POE_SECRET_NAME=akkadian-talker-archon-secret POE_BOT_NAME=AkkadianArchon modal deploy main.py
SECRET_NAME = os.environ.get("POE_SECRET_NAME", "akkadian-talker-secret")
POE_BOT_NAME = os.environ.get("POE_BOT_NAME", "")

# Bake POE_BOT_NAME and BOT_MODEL into the image so they're available inside the
# container at runtime, not just locally at deploy time. Without this, the container's
# `BOT = os.environ.get("BOT_MODEL", ...)` would fall back to its default.
# .env() must come before add_local_python_source().
image = (
    Image.debian_slim()
    .pip_install_from_requirements("requirements.txt")
    .env({"POE_BOT_NAME": POE_BOT_NAME, "BOT_MODEL": BOT})
    .add_local_python_source("akkadian_talker_bot", "corpus", "prompt")
)
app = App(f"akkadian-talker-{BOT}")


@app.function(image=image, secrets=[Secret.from_name(SECRET_NAME)])
@asgi_app()
def fastapi_app():
    access_key = os.environ.get("POE_ACCESS_KEY", "")
    if not access_key:
        raise RuntimeError(
            f"POE_ACCESS_KEY is not set (or empty) in Modal secret '{SECRET_NAME}'. "
            "Edit the secret in the Modal dashboard and set it to the 32-char access key "
            "from your bot's edit page on poe.com."
        )
    if not POE_BOT_NAME:
        raise RuntimeError(
            "POE_BOT_NAME env var is required at deploy time so the bot instance "
            "knows its Poe-side name (e.g. AkkadianOracle). Redeploy with: "
            "POE_BOT_NAME=AkkadianOracle POE_SECRET_NAME=... modal deploy main.py"
        )
    bot = AkkadianTalkerBot(access_key=access_key, bot_name=POE_BOT_NAME)
    return make_app(bot, allow_without_key=True)

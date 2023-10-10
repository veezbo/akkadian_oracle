import os

from fastapi_poe import make_app
from modal import Image, Secret, Stub, asgi_app

from akkadian_talker_bot import AkkadianTalkerBot, BOT

# Specific to hosting with modal.com
image = Image.debian_slim().pip_install_from_requirements("requirements.txt")
stub = Stub(f"akkadian-talker-{BOT}")


@stub.function(image=image, secret=Secret.from_name("akkadian-talker-secret"))
@asgi_app()
def fastapi_app():
    bot = AkkadianTalkerBot()
    app = make_app(bot, access_key=os.environ["POE_ACCESS_KEY"], api_key=os.environ["POE_API_KEY"])
    return app

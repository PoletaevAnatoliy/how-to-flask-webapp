#!/usr/bin/env python3
import os
from dotenv import load_dotenv

from webapp import create_app

load_dotenv(".env")
app = create_app()
app.run(port=int(os.environ.get("FLASK_RUN_PORT")))

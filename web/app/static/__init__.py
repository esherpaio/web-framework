import os

from web.packer.bundle import JsBundle

_dir = os.path.dirname(os.path.abspath(__file__))
js_bundle = JsBundle(_dir)

import json
import os
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit, SplitResult
from dataclasses import asdict
import scrapy

from kuntavaalit.items import *


class KuntavaalitPipeline:
    def process_item(self, item: Item, spider: scrapy.Spider):
        if not isinstance(item, Item):
            return

        basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "items"))
        fullpath = None

        if isinstance(item, Item):
            if isinstance(item, ItemWithMunicipality):
                basepath = os.path.abspath(os.path.join(basepath, str(item.municipality)))

            fname = type(item).__name__.lower()

            if isinstance(item, Answer):
                fname += '_' + str(item.candidateid)

            fname += ".json"

            fullpath = os.path.abspath(os.path.join(basepath, fname))

        if fullpath is None:
            return

        Path(basepath).mkdir(parents=True, exist_ok=True)

        if os.path.isfile(fullpath):
            spider.logger.warning(f"file '{fullpath}' exists, skipping!")
            return

        # Save to temporary file
        tmpf = NamedTemporaryFile("w", prefix="yle-kv-", suffix=".json", encoding="utf8", delete=False)
        with tmpf as f:
            json.dump(asdict(item)['data'], f)
            f.flush()
            spider.logger.info(f"saved as {f.name}")

        # Rename and move the temporary file to actual file
        newpath = move(tmpf.name, fullpath)
        spider.logger.info(f"renamed {tmpf.name} to {newpath}")

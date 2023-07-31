import json

import msgpack
import requests

from data_zipcaster import __version__
from data_zipcaster.cli.base_plugins import BaseExporter
from data_zipcaster.exporters.splashcat.convert import convert
from data_zipcaster.schemas.vs_modes import VsExtractDict


class SplashcatExporter(BaseExporter):
    @property
    def name(self) -> str:
        return "splashcat"

    @property
    def help(self) -> str:
        return "Exports data to Splashcat.\n\n"

    def get_config_keys(self) -> list[BaseExporter.ConfigKeys]:
        keys = [
            BaseExporter.ConfigKeys(
                key_name="api_key",
                help=(
                    "The API key to use for the Splashcat API. "
                    "This key is required."
                ),
                type_=str,
                required=True,
            ),
        ]
        return keys

    def do_run(self, data: list[VsExtractDict]) -> None:
        api_key = self.get_from_config(self.name, "api_key")
        out: list[dict] = []
        self.vprint("Processing data...", level=2)
        for battle in data:
            out.append(self.process_battle(battle))
        self.vprint("Uploading data to Splashcat...", level=1)
        self.vprint("Starting session...", level=3)
        session = requests.Session()
        self.vprint("Building headers...", level=2)
        headers = {
            "Content-Type": "application/x-msgpack",
            "Authorization": f"Bearer {api_key}",
        }
        self.vprint("Getting existing battle IDs...", level=2)
        existing_ids = session.get(
            "https://splashcat.ink/battles/api/recent/",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        ).json()["battle_ids"]
        self.vprint("Encoding data...", level=2)
        count = 0
        for body in out:
            if ("battle" in body) and (
                body["battle"]["splatnetId"] in existing_ids
            ):
                continue
            msg = msgpack.packb(body)
            self.vprint("Uploading data...", level=2)
            response = session.post(
                "https://splashcat.ink/battles/api/upload/",
                data=msg,
                headers=headers,
            )
            # Temporarily save the data to a file
            with open(f"data{count}.json", "w") as f:
                json.dump(body, f)
            count += 1

    def process_battle(self, battle: VsExtractDict) -> dict:
        return {
            "battle": convert(battle),
            "data_type": "splashcat",
            "uploader_agent": {
                "name": "data-zipcaster",
                "version": __version__,
                "extra": "exporter",
            },
        }

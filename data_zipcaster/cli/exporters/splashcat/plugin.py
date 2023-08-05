from typing import cast

import msgpack
import requests

from data_zipcaster import __version__
from data_zipcaster.cli.base_plugins import BaseExporter
from data_zipcaster.cli.utils import ProgressBar
from data_zipcaster.models import main
from data_zipcaster.utils import base64_encode
from data_zipcaster.views.splashcat import generate_view


class Endpoints:
    recent_battles = "https://splashcat.ink/battles/api/recent/"
    upload_battle = "https://splashcat.ink/battles/api/upload/"


class SplashcatExporter(BaseExporter):
    def __init__(self) -> None:
        super().__init__()
        self.silent: bool = False
        self.api_key: str = ""
        self.headers: dict = {}
        self.session: requests.Session | None = None

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

    def do_run(self, data: list[main.VsExtract]) -> None:
        self.set_values_from_config()

        self.session = self.start_session()
        self.headers = self.build_headers()

        self.vprint("Getting existing battle IDs...", level=1)
        existing_ids = self.get_existing_battle_ids()

        self.vprint("Uploading data to Splashcat...", level=1)
        self.process_data(data, existing_ids)

    def set_values_from_config(self) -> None:
        self.api_key = self.get_from_config(self.name, "api_key")

    def start_session(self) -> requests.Session:
        self.vprint("Starting session...", level=3)
        return requests.Session()

    def build_headers(self) -> dict:
        self.vprint("Building headers...", level=2)
        return {
            "Content-Type": "application/x-msgpack",
            "Authorization": f"Bearer {self.api_key}",
        }

    def process_data(
        self, data: list[main.VsExtract], existing_ids: list[str]
    ) -> list[dict]:
        with ProgressBar("Processing data...") as progress_callback:
            max_val = len(data)
            progress_callback(0, max_val)
            if self.get_from_context("imported") is None:
                self.set_to_context("imported", [])

            for idx, battle in enumerate(data):
                body = self.process_battle(battle)
                self.upload_match(body, existing_ids)
                imported = cast(list[str], self.get_from_context("imported"))
                if battle.id not in imported:
                    imported.append(base64_encode(battle.id))

                if progress_callback is not None:
                    progress_callback(idx + 1, max_val)

    def process_battle(self, battle: main.VsExtract) -> dict:
        return {
            "battle": generate_view(battle),
            "data_type": "splashcat",
            "uploader_agent": {
                "name": "data-zipcaster",
                "version": __version__,
                "extra": "exporter",
            },
        }

    def upload_match(self, body: dict, existing_ids: list[str]) -> None:
        assert self.session is not None
        if ("battle" in body) and (
            body["battle"]["splatnetId"] in existing_ids
        ):
            return

        msg = msgpack.packb(body)
        response = self.session.post(
            Endpoints.upload_battle,
            data=msg,
            headers=self.headers,
        )
        if response.status_code != 200:
            raise ValueError(f"Error uploading match: {response.text}")

    def get_existing_battle_ids(self) -> list[str]:
        self.vprint("Getting existing battle IDs...", level=2)
        assert self.session is not None
        return self.session.get(
            Endpoints.recent_battles,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        ).json()["battle_ids"]

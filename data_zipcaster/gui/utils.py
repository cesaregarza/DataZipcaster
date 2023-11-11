from __future__ import annotations

import configparser as cp
import logging
import os
from typing import Callable, ParamSpec, TypeVar, cast

from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal
from splatnet3_scraper.constants import TOKENS
from splatnet3_scraper.query import QueryHandler
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.constants import IMINK_URL, NXAPI_URL
from data_zipcaster.gui.exceptions import CancelFetchException

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

T = TypeVar("T")
P = ParamSpec("P")


class SplatNet_Scraper_Wrapper(QObject):
    testing_finished = pyqtSignal(bool)
    progress_outer_changed = pyqtSignal(int, int)
    progress_inner_changed = pyqtSignal(int, int)
    fetching_started = pyqtSignal()
    fetching_finished = pyqtSignal(dict)

    def __init__(self, scraper: SplatNet_Scraper) -> None:
        super().__init__()
        if not isinstance(scraper, SplatNet_Scraper):
            raise TypeError(
                f"Expected SplatNet_Scraper, got {type(scraper).__name__}"
            )
        self.scraper = scraper
        self.cancelled = False
        logging.debug("SplatNet_Scraper_Wrapper initialized")

    @staticmethod
    def scraper_decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(self: "SplatNet_Scraper_Wrapper", *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.moveToThread(QCoreApplication.instance().thread())
            return result

        return wrapper

    @scraper_decorator
    def test_tokens(self) -> None:
        logging.info("Testing tokens")
        result = self.test_tokens_blocking()
        logging.debug("Emitting testing_finished signal")
        self.testing_finished.emit(result)

    def test_tokens_blocking(self) -> bool:
        try:
            handler = self.scraper.query_handler
            handler.query(
                "HomeQuery",
                variables={
                    "language": "en-US",
                    "naCountry": "US",
                },
            )
            return True
        except Exception as e:
            logging.exception("Error while testing tokens")
            logging.debug("Error: %s", e)
            return False

    @classmethod
    def from_config(cls, config_path: str) -> SplatNet_Scraper_Wrapper:
        config = cp.ConfigParser()
        config.read(config_path)
        splatnet = config["splatnet"]

        session_token = splatnet.get("session_token")
        gtoken = splatnet.get("gtoken", None)
        bullet_token = splatnet.get("bullet_token", None)

        ftoken_url = splatnet.get("ftoken_url", f"{IMINK_URL},{NXAPI_URL}")
        ftoken_urls = cast(list[str], ftoken_url.split(","))

        query_handler = QueryHandler.from_tokens(
            session_token, gtoken, bullet_token
        )
        query_handler.config.token_manager.f_token_url = ftoken_urls
        return cls(SplatNet_Scraper(query_handler))

    @classmethod
    def from_session_token(cls, session_token: str) -> SplatNet_Scraper_Wrapper:
        scraper = SplatNet_Scraper.from_session_token(session_token)
        scraper.query_handler.config.token_manager.f_token_url = [
            IMINK_URL,
            NXAPI_URL,
        ]
        return cls(scraper)

    @classmethod
    def from_s3s_config(cls, config_path: str) -> SplatNet_Scraper_Wrapper:
        scraper = SplatNet_Scraper.from_s3s_config(config_path)
        scraper.query_handler.config.token_manager.f_token_url = [
            IMINK_URL,
            NXAPI_URL,
        ]
        return cls(scraper)

    def save_config(self, config_path: str) -> None:
        """Save the config to a file.

        Args:
            config_path (str): The path to the config file.
        """
        logging.debug("Saving config")
        config = cp.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)

        if "splatnet" not in config:
            config["splatnet"] = {}

        scraper_config = self.scraper.query_handler.config
        for value_name in [
            TOKENS.SESSION_TOKEN,
            TOKENS.GTOKEN,
            TOKENS.BULLET_TOKEN,
            "ftoken_url",
        ]:
            value = scraper_config.get_value(value_name)
            if isinstance(value, list):
                value = ",".join(value)
            config["splatnet"][value_name] = value

        with open(config_path, "w") as f:
            logging.debug("Writing config file")
            config.write(f)
        logging.info("Config saved")

    @scraper_decorator
    def fetch_data(
        self,
        anarchy: bool = False,
        private: bool = False,
        turf_war: bool = False,
        x_battle: bool = False,
        challenge: bool = False,
        salmon_run: bool = False,
        limit: int = 50,
    ) -> None:
        """Fetch data from SplatNet.

        Args:
            anarchy (bool, optional): Whether to fetch data for anarchy modes.
                Defaults to False.
            private (bool, optional): Whether to fetch data for private battles.
                Defaults to False.
            turf_war (bool, optional): Whether to fetch data for turf war.
                Defaults to False.
            x_battle (bool, optional): Whether to fetch data for X battles.
                Defaults to False.
            challenge (bool, optional): Whether to fetch data for challenge
                modes. Defaults to False.
            limit (int, optional): The maximum number of battles to fetch.
                Defaults to 50.

        Returns:
            dict: The data fetched from SplatNet.
        """
        logging.debug("Fetching data")
        logging.debug("Anarchy: %s", anarchy)
        logging.debug("Private: %s", private)
        logging.debug("Turf War: %s", turf_war)
        logging.debug("X Battle: %s", x_battle)
        logging.debug("Challenge: %s", challenge)
        logging.debug("Limit: %s", limit)
        self.cancelled = False
        self.fetching_started.emit()
        try:
            self.fetch(
                anarchy=anarchy,
                private=private,
                turf_war=turf_war,
                x_battle=x_battle,
                challenge=challenge,
                salmon_run=salmon_run,
                limit=limit,
            )
        except CancelFetchException:
            logging.debug("Fetch cancelled")
            self.fetching_finished.emit({})

    def fetch(
        self,
        anarchy: bool = False,
        private: bool = False,
        turf_war: bool = False,
        x_battle: bool = False,
        challenge: bool = False,
        salmon_run: bool = False,
        limit: int = 50,
    ) -> None:
        logging.debug("Fetching data")
        self.cancelled = False

        flags = [
            # (flag, name, print name)
            (anarchy, "anarchy", "Anarchy Battles"),
            (private, "private", "Private Battles"),
            (turf_war, "turf", "Turf War"),
            (x_battle, "xbattle", "X Battles"),
            (challenge, "challenge", "Challenges"),
            (salmon_run, "salmon_run", "Salmon Run"),
        ]
        flags = [(name, print_name) for flag, name, print_name in flags if flag]
        logging.debug("Fetching: %s", flags)
        out = {}
        for i, (name, print_name) in enumerate(flags):
            logging.debug("Fetching %s", print_name)
            self.progress_outer_changed.emit(i, len(flags))
            data = self.scraper.get_matches(
                name,
                detail=True,
                limit=limit,
                progress_callback=self.progress_callback,
            )
            logging.debug("Fetched %s", print_name)
            out[name] = data
        logging.debug("Emitting fetching_finished signal")
        self.fetching_finished.emit(out)

    def progress_callback(self, current: int, total: int) -> None:
        logging.debug("Progress: %s/%s", current, total)
        if self.cancelled:
            logging.debug("Detected cancellation, raising CancelFetchException")
            raise CancelFetchException()
        self.progress_inner_changed.emit(current, total)

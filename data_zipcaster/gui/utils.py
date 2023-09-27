import configparser as cp
import logging
import os
from typing import Callable, ParamSpec, TypeVar, cast

from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal
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
    def from_config(cls, config_path: str) -> "SplatNet_Scraper_Wrapper":
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
    def from_session_token(
        cls, session_token: str
    ) -> "SplatNet_Scraper_Wrapper":
        scraper = SplatNet_Scraper.from_session_token(session_token)
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

        token_manager = self.scraper.query_handler.config.token_manager
        config["splatnet"]["session_token"] = token_manager.get("session_token")
        config["splatnet"]["gtoken"] = token_manager.get("gtoken")
        config["splatnet"]["bullet_token"] = token_manager.get("bullet_token")
        config["splatnet"]["ftoken_url"] = ",".join(token_manager.f_token_url)
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
            self.simulated_fetch()
        except CancelFetchException:
            logging.debug("Fetch cancelled")
            self.fetching_finished.emit({})

    def simulated_fetch(self) -> None:
        logging.debug("Simulating fetch")
        self.cancelled = False
        import time

        counter = 10
        self.progress_outer_changed.emit(0, 1)
        self.progress_inner_changed.emit(0, 10)
        while counter > 0:
            logging.debug("Counter: %s", counter)
            time.sleep(1)
            counter -= 1
            self.progress_inner_changed.emit(10 - counter, 10)
            if self.cancelled:
                logging.debug("SIMULATED Cancelled")
                raise CancelFetchException()
        self.fetching_finished.emit({})

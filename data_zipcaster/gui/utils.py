import configparser as cp
import logging
import os
from typing import cast

from PyQt5.QtCore import QObject, pyqtSignal
from splatnet3_scraper.query import QueryHandler
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.constants import IMINK_URL, NXAPI_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SplatNet_Scraper_Wrapper(QObject):
    testing_started = pyqtSignal()
    testing_finished = pyqtSignal(bool)

    def __init__(self, scraper: SplatNet_Scraper) -> None:
        super().__init__()
        self.scraper = scraper
        logging.debug("SplatNet_Scraper_Wrapper initialized")

    def test_tokens(self) -> None:
        logging.info("Testing tokens")
        logging.debug("Emitting testing_started signal")
        self.testing_started.emit()
        try:
            handler = self.scraper.query_handler
            handler.query(
                "HomeQuery",
                variables={
                    "language": "en-US",
                    "naCountry": "US",
                },
            )
        except Exception:
            logging.exception("Error while testing tokens")
            self.testing_finished.emit(False)
        else:
            logging.debug("Emitting testing_finished signal")
            self.testing_finished.emit(True)

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
        logger.debug("Saving config")
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
            logger.debug("Writing config file")
            config.write(f)
        logger.info("Config saved")

    def fetch_data(
        self,
        anarchy: bool = False,
        private: bool = False,
        turf_war: bool = False,
        x_battle: bool = False,
        challenge: bool = False,
        limit: int = 50,
    ) -> dict:
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
        logger.debug("Fetching data")

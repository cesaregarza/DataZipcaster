import configparser as cp
from typing import cast

from PyQt5.QtCore import QObject, pyqtSignal
from splatnet3_scraper.auth import TokenManager
from splatnet3_scraper.query import QueryHandler
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.constants import IMINK_URL, NXAPI_URL


class SplatNet_Scraper_Wrapper(QObject):
    testing_started = pyqtSignal()
    testing_finished = pyqtSignal(bool)

    def __init__(self, scraper: SplatNet_Scraper) -> None:
        super().__init__()
        self.scraper = scraper

    def test_tokens(self) -> None:
        self.testing_started.emit()
        try:
            self.scraper.query_handler.config.token_manager.test_tokens()
        except Exception:
            self.testing_finished.emit(False)
        else:
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

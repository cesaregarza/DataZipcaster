from splatnet3_scraper.constants import TOKENS
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.base_plugin import BasePlugin


class SplatNetImporter(BasePlugin):
    @property
    def name(self):
        return "splatnet"

    @property
    def help(self):
        return (
            "Imports data from SplatNet 3. This is the default importer.  "
            + "This requires one of the following arguments:  "
            + " - `--env` to use environment variables to load your SplatNet 3 "
            + "tokens. "
            + " - `--session-token` to load your SplatNet 3 session token "
            + "directly from the command line. "
            + " - `--config` to load your SplatNet 3 tokens from a config "
            + "file. If no path is specified, the default path is "
            + "[bold yellow].splatnet3_scraper[/] in the current directory."
        )

    @property
    def requires_config(self):
        return True

    def get_scraper(self, config_data: dict[str, str]) -> SplatNet_Scraper:
        session_token = config_data.get(TOKENS.SESSION_TOKEN, None)
        gtoken = config_data.get(TOKENS.GTOKEN, None)
        bullet_token = config_data.get(TOKENS.BULLET_TOKEN, None)
        env_vars = config_data.get("env_vars", False)

        if env_vars:
            return SplatNet_Scraper.from_env()
        elif session_token is not None:
            out = SplatNet_Scraper.from_session_token(session_token)
            token_manager = out._query_handler.config.token_manager
            if gtoken is not None:
                token_manager.add_token(gtoken, TOKENS.GTOKEN)
            if bullet_token is not None:
                token_manager.add_token(bullet_token, TOKENS.BULLET_TOKEN)
            return out
        else:
            raise ValueError(
                "No session token was provided. Please provide a session token "
                + "by adding ``session_token = <your session token>`` to the "
                + "``[splatnet]`` section of your config file"
            )

    def do_run(
        self,
        config: dict[str, dict[str, str]],
        flags: dict[str, bool],
        *args,
        **kwargs,
    ):
        settings = config.get("settings", None)
        config_data = config[self.name]

        scraper = self.get_scraper(config_data)

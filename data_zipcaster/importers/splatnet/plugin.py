import logging
import os
from typing import Callable

import rich_click as click
from rich.progress import Progress
from splatnet3_scraper.auth.exceptions import (
    FTokenException,
    NintendoException,
    SplatNetException,
)
from splatnet3_scraper.query import QueryHandler, QueryResponse
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.base_plugins import BaseImporter
from data_zipcaster.cli import styles as s
from data_zipcaster.cli.utils import ProgressBar


class SplatNetImporter(BaseImporter):
    @property
    def name(self) -> str:
        return "splatnet"

    @property
    def help(self) -> str:
        return (
            "Imports data from SplatNet 3. This is the default importer.\n\n"
            "This requires one of the following arguments: \n\n"
            " * --session-token to load your SplatNet 3 session token "
            "directly from the command line. \n\n"
            " * --config to load your SplatNet 3 tokens from a config "
            "file. If no path is specified, the default path is "
            f"{s.EMPHASIZE}config.ini[/] in the current directory. \n\n"
            "If neither of these are specified, the importer will "
            "attempt to load your SplatNet 3 session token from the "
            f"environment variable {s.ENVVAR_COLOR}SESSION_TOKEN[/], "
            "\n"
            "If you do not have a SplatNet 3 session token, you can "
            "generate one by following the instructions at "
        )

    def get_options(self) -> list[BaseImporter.Options]:
        options = [
            BaseImporter.Options(
                option_name_1="-s",
                option_name_2="--salmon",
                is_flag=True,
                help="Import Salmon Run data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-x",
                option_name_2="--xbattle",
                is_flag=True,
                help="Import XBattle data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-t",
                option_name_2="--turf",
                is_flag=True,
                help="Import Turf War data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-n",
                option_name_2="--anarchy",
                is_flag=True,
                help="Import Anarchy data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-p",
                option_name_2="--private",
                is_flag=True,
                help="Import Private Battle data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-c",
                option_name_2="--challenge",
                is_flag=True,
                help="Import Challenge data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="-a",
                option_name_2="--all",
                is_flag=True,
                help="Import all data.",
                default=False,
            ),
            BaseImporter.Options(
                option_name_1="--config",
                type_=click.Path(exists=False, dir_okay=False),
                help=(
                    "Path to the config file. If not specified, the default "
                    f"path is {s.EMPHASIZE}config.ini[/] in the current "
                    "directory."
                ),
                default=os.path.join(os.getcwd(), "config.ini"),
            ),
            BaseImporter.Options(
                option_name_1="--gtoken",
                type_=str,
                help=("Your Nintendo Switch Online G-token."),
                default=None,
                nargs=1,
                envvar="GTOKEN",
            ),
            BaseImporter.Options(
                option_name_1="--bullet-token",
                type_=str,
                help=("Your Splatnet bullet token."),
                default=None,
                nargs=1,
                envvar="BULLET_TOKEN",
            ),
            BaseImporter.Options(
                option_name_1="--session-token",
                type_=str,
                help=("Your Nintendo Switch Online session token."),
                default=None,
                nargs=1,
                envvar="SESSION_TOKEN",
            ),
        ]
        return options

    def do_run(
        self,
        **kwargs,
    ):
        session_token = kwargs.get("session_token", None)
        gtoken = kwargs.get("gtoken", None)
        bullet_token = kwargs.get("bullet_token", None)
        scraper = self.get_scraper(session_token, gtoken, bullet_token)

        silent = kwargs.get("silent", False)
        self.test_tokens(scraper, silent)
        self.parse_flags(kwargs)
        outs = []
        message = f"Importing data from SplatNet 3..."
        with ProgressBar(message) as progress_callback:
            outs.append(
                self.get_vs_battles(
                    scraper,
                    "xbattle",
                    limit=10,
                    progress_callback=progress_callback,
                )
            )

        return 6

    def test_tokens(
        self, scraper: SplatNet_Scraper, silent: bool = False
    ) -> None:
        handler = scraper._query_handler

        def fxn() -> None:
            handler.query(
                "HomeQuery",
                variables={
                    "language": "en-US",
                    "naCountry": "US",
                },
            )

        if silent:
            fxn()
            return

        with Progress(transient=True) as progress:
            task = progress.add_task("Testing session token...", total=None)
            fxn()

    def get_scraper(
        self,
        session_token: str,
        gtoken: str | None = None,
        bullet_token: str | None = None,
    ) -> SplatNet_Scraper:
        handler = QueryHandler.from_tokens(session_token, gtoken, bullet_token)
        return SplatNet_Scraper(handler)

    def get_vs_battles(
        self,
        scraper: SplatNet_Scraper,
        mode: str,
        limit: int | None = None,
        progress_callback: Callable[[int, int], None] = None,
    ) -> tuple[QueryResponse, list[QueryResponse]]:
        try:
            overview, detailed = scraper.get_vs_battles(
                mode, True, limit, progress_callback=progress_callback
            )
        except NintendoException:
            raise click.ClickException(
                "Failed to log in. This is likely due to an invalid "
                "session token. Please check your session token and try "
                "again."
            )
        except FTokenException as e:
            raise click.ClickException(
                "Failed to generate f-token. This is likely due to the f-token "
                "server being down and is out of your control. Please try "
                "again later."
            )
        except SplatNetException as e:
            # Check the error code within the exception message
            message = e.args[0]
            if "401" in message:
                raise click.ClickException(
                    "Failed to log in. This is a very very rare error that "
                    "is resolved by simply trying again. Please try again."
                )
            elif "403" in message:
                raise click.ClickException(
                    "Obsolete version. Please update this program to the "
                    "latest version and try again."
                )
            elif "204" in message:
                raise click.ClickException(
                    "Failed to log in. The account you are using has not "
                    "played Splatoon 3 online. Please either log in with an "
                    "account that has played at least one match of Splatoon 3 "
                    "online, or use a session token from an account that has "
                    "played at least one match of Splatoon 3 online."
                )

        tokens = scraper._query_handler.export_tokens()
        for token_type, token in tokens:
            if token_type == "session_token":
                continue

            if self.get_from_config(self.name, token_type) != token:
                self.set_to_config(self.name, token_type, token)
        self.save_config()
        return overview, detailed

    def parse_flags(self, kwargs: dict) -> None:
        flag_all = kwargs.get("all", False)
        flag_salmon = kwargs.get("salmon", False)
        flag_xbattle = kwargs.get("xbattle", False)
        flag_turf = kwargs.get("turf", False)
        flag_anarchy = kwargs.get("anarchy", False)
        flag_private = kwargs.get("private", False)
        flag_challenge = kwargs.get("challenge", False)

        flags = self.manage_flags(
            flag_all,
            flag_salmon,
            flag_xbattle,
            flag_turf,
            flag_anarchy,
            flag_private,
            flag_challenge,
        )

        kwargs["all"] = flags[0]
        kwargs["salmon"] = flags[1]
        kwargs["xbattle"] = flags[2]
        kwargs["turf"] = flags[3]
        kwargs["anarchy"] = flags[4]
        kwargs["private"] = flags[5]
        kwargs["challenge"] = flags[6]

    def manage_flags(
        self,
        flag_all: bool,
        flag_salmon: bool,
        flag_xbattle: bool,
        flag_turf: bool,
        flag_anarchy: bool,
        flag_private: bool,
        flag_challenge: bool,
    ) -> tuple[bool, bool, bool, bool, bool, bool, bool]:
        non_all_flags = [
            flag_salmon,
            flag_xbattle,
            flag_turf,
            flag_anarchy,
            flag_private,
            flag_challenge,
        ]
        # This will be True if all is True, or if all the flags are True
        flag_all = (flag_all) or all(non_all_flags)

        # If all the flags are false, then set all to True
        if not any(non_all_flags):
            flag_all = True

        # If all is True, then set all the flags to True
        if flag_all:
            flag_salmon = True
            flag_xbattle = True
            flag_turf = True
            flag_anarchy = True
            flag_private = True
            flag_challenge = True

        return (
            flag_all,
            flag_salmon,
            flag_xbattle,
            flag_turf,
            flag_anarchy,
            flag_private,
            flag_challenge,
        )

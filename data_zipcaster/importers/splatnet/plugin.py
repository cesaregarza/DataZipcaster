import os

import rich_click as click
from splatnet3_scraper.auth.exceptions import (
    FTokenException,
    NintendoException,
    SplatNetException,
)
from splatnet3_scraper.constants import TOKENS
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.base_plugins import BaseImporter
from data_zipcaster.cli import styles as s


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
        try:
            scraper = SplatNet_Scraper.from_session_token(session_token)
        except NintendoException:
            raise click.ClickException(
                "Failed to log in. This is likely due to an invalid "
                "session token. Please check your session token and try "
                "again."
            )
        except FTokenException:
            raise click.ClickException(
                "Failed to generate f-token. This is likely due to the f-token "
                "server being down and is out of your control. Please try "
                "again later."
            )

        self.parse_flags(kwargs)
        return 6

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

import json
import os
import time
from typing import Callable, ParamSpec, TypeVar, cast

import rich_click as click
from splatnet3_scraper.auth.exceptions import (
    FTokenException,
    NintendoException,
    SplatNetException,
)
from splatnet3_scraper.query import QueryResponse
from splatnet3_scraper.scraper import SplatNet_Scraper

from data_zipcaster.cli import constants as consts
from data_zipcaster.cli import styles as s
from data_zipcaster.cli.base_plugins import BaseImporter
from data_zipcaster.cli.utils import ProgressBar
from data_zipcaster.models import main, splatnet
from data_zipcaster.transforms import splatnet_to_main as transforms

T = TypeVar("T")
P = ParamSpec("P")


class SplatNetImporter(BaseImporter):
    def __init__(self) -> None:
        super().__init__()
        self.session_token: str = ""
        self.gtoken: str | None = None
        self.bullet_token: str | None = None
        self.silent: bool = False
        self.limit: int = -1

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

    @property
    def include_monitoring(self) -> bool:
        return True

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
                option_name_1="-a",
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
                option_name_1="--all",
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
                option_name_1="--limit",
                type_=int,
                help=(
                    "The maximum number of battles to import. If not "
                    "specified, all battles will be imported."
                ),
                default=-1,
            ),
            BaseImporter.Options(
                option_name_1="--save-raw",
                help=(
                    "Save the raw data from the query. Takes one argument, "
                    "which is the path to the directory to save the raw data "
                    "to. If the path is relative, it will be relative to the "
                    "current working directory. It will be saved to a "
                    "directory with the current time as the name, and then "
                    "subdirectories for each mode. The raw data will be saved "
                    "as JSON files. If not specified, the raw data will not "
                    "be saved. Having this option enabled is the only way to "
                    "import from splatnet without specifying an "
                    f"{s.EXPORTER_COLOR}exporter[/]."
                ),
                default=None,
                nargs=1,
                type_=click.Path(exists=False, file_okay=False),
            ),
            BaseImporter.Options(
                option_name_1="--f-token-url",
                type_=str,
                help=(
                    "The URL to the f-token server. If not specified, the "
                    "default URL is "
                    f"{s.EMPHASIZE}https://api.imink.app/f[/]."
                ),
                default="https://api.imink.app/f",
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
    ) -> list[main.VsExtract]:
        """Runs the importer. This is the main function of the importer, it is
        called automatically by ``BaseImporter.run``.

        This function will parse the kwargs, get a scraper, test the tokens,
        parse the flags, print the flags that are being imported, and then
        process the data.

        Args:
            **kwargs: The kwargs passed to the run function.

        Returns:
            list[main.VsExtract]: The imported data.
        """
        self.parse_kwargs(kwargs)
        scraper = self.get_scraper()
        self.test_tokens(scraper)
        self.parse_flags(kwargs)
        self.print_importing_flags(kwargs)

        return self.process_data(scraper, kwargs)

    def parse_kwargs(self, kwargs: dict) -> None:
        session_token = kwargs.get("session_token", None)
        gtoken = kwargs.get("gtoken", None)
        bullet_token = kwargs.get("bullet_token", None)
        silent = kwargs.get("silent", False)
        limit = kwargs.get("limit", None)

        if session_token is None:
            raise click.ClickException(
                "No session token was specified. Please specify a session "
                "token with the --session-token flag, or use the --config "
                "flag to load your tokens from a config file. If you have a "
                "config file, make sure you've specified the correct path."
            )

        # Set as self attributes
        self.session_token = cast(str, session_token)
        self.gtoken = cast(str | None, gtoken)
        self.bullet_token = cast(str | None, bullet_token)
        self.silent = cast(bool, silent)
        self.limit = cast(int, limit)

    def test_tokens(self, scraper: SplatNet_Scraper) -> None:
        """Tests the session token to make sure it is valid.

        Tests the tokens loaded onto the scraper to make sure they are valid by
        making a fast, simple query. If the query fails, the scraper will
        automatically attempt to refresh the tokens. Also generates a progress
        bar that will be overwritten once this function is done. If silent is
        True, the progress bar will not be generated. Silent is set by the
        parse_kwargs function.

        Args:
            scraper (SplatNet_Scraper): The scraper to test the tokens on.
        """
        handler = scraper.query_handler

        def fxn() -> None:
            self.handle_scraper_errors(
                handler.query,
                "HomeQuery",
                variables={
                    "language": "en-US",
                    "naCountry": "US",
                },
            )
            self.save_tokens(scraper)

        self.progress_bar(
            fxn,
            message="Testing and refreshing tokens...",
            condition=self.silent,
            transient=True,
        )

    def get_scraper(
        self,
    ) -> SplatNet_Scraper:
        """Gets a scraper with the given tokens.

        Calls on the following attributes set by the parse_kwargs function:

        - session_token (str): The session token to use. This is the only
            required token.
        - gtoken (str | None): The gtoken to use. Defaults to None.
        - bullet_token (str | None): The bullet token to use. Defaults to None.
        - silent (bool): Whether or not to suppress the progress bar. Defaults
            to False.

        Any missing tokens will be generated by the scraper. The tokens will
        also be saved to the config file. All output will be suppressed if
        silent is True.

        Returns:
            SplatNet_Scraper: The scraper with the given tokens.
        """

        def fxn() -> SplatNet_Scraper:
            scraper = SplatNet_Scraper.from_tokens(
                self.session_token, self.gtoken, self.bullet_token
            )
            self.save_tokens(scraper)
            return scraper

        condition = ((self.gtoken is None) or (self.bullet_token is None)) and (
            not self.silent
        )
        return self.progress_bar(
            fxn,
            message="Generating missing tokens...",
            condition=condition,
            transient=True,
        )

    def __get_matches(
        self,
        scraper: SplatNet_Scraper,
        mode: str,
        limit: int | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
        existing_ids: list[str] | None = None,
    ) -> tuple[QueryResponse, list[QueryResponse]]:
        """Gets the vs battles from the scraper.

        Gets the vs battles from the scraper. This will also update the tokens
        in the config file if they have changed as a result of the query, which
        automatically happens when the scraper refreshes the tokens on a failed
        query. Additionally, this will convert exceptions into click exceptions
        with helpful messages for the user.

        Args:
            scraper (SplatNet_Scraper): The scraper to get the vs battles from.
            mode (str): The mode to get the vs battles from.
            limit (int | None): The maximum number of battles to get. Defaults
                to None.
            progress_callback (Callable[[int, int], None]): A callback to
                update the progress bar. Defaults to None.

        Returns:
            tuple[QueryResponse, list[QueryResponse]]: The overview and
                detailed vs battles.
        """
        overview, detailed = self.handle_scraper_errors(
            scraper.get_matches,
            mode,
            True,
            limit,
            progress_callback=progress_callback,
            existing_ids=existing_ids,
        )

        self.save_tokens(scraper)
        return overview, detailed

    def handle_scraper_errors(
        self, fxn: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        """Wraps a function to handle scraper errors.

        Args:
            fxn (Callable[P, T]): The function to wrap.
            *args (P.args): The positional arguments to pass to the function.
            **kwargs (P.kwargs): The keyword arguments to pass to the function.

        Raises:
            ClickException: When the session token is invalid.
            ClickException: When the f-token server is down.
            ClickException: Error 401
            ClickException: Error 403
            ClickException: Error 204
            Exception: Any other exception.

        Returns:
            T: The return value of the function.
        """
        try:
            return fxn(*args, **kwargs)
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
        except Exception as e:
            raise e

        # It should never reach this point, but mypy doesn't know that
        return cast(T, None)

    def save_tokens(self, scraper: SplatNet_Scraper) -> None:
        """Saves the tokens to the config file.

        Saves the tokens to the config file. This will only save the tokens
        that have changed since the last time the tokens were saved.

        Args:
            scraper (SplatNet_Scraper): The scraper to get the tokens from.
        """
        tokens = scraper.query_handler.export_tokens()
        for token_type, token in tokens:
            if token_type == "session_token":
                continue

            if self.get_from_config(self.name, token_type) != token:
                self.set_to_config(self.name, token_type, token)
        self.save_config()

    def parse_flags(self, kwargs: dict) -> None:
        """Parses the flags to determine which modes to import.

        Resolves logic between the flags to determine which modes to import. If
        all is True, then all the flags are set to True. If all the flags are
        True, then all is set to True. Mutates the kwargs dict.


        Args:
            kwargs (dict): The kwargs passed to the run function.
        """
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

    def print_importing_flags(self, kwargs: dict) -> None:
        """Prints the flags that are being imported.

        Args:
            kwargs (dict): The kwargs passed to the run function.
        """
        # Print the flags that are being imported
        true_flags = [
            consts.FLAG_MAP[flag] for flag in consts.FLAG_LIST if kwargs[flag]
        ]
        join_str = f"[/], {s.OPTION_COLOR}"
        self.vprint(
            f"Importing {s.OPTION_COLOR}{join_str.join(true_flags)}[/] "
            "data from SplatNet 3...",
            level=0,
        )

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
        """Manages the flags to determine which modes to import.

        Contains the logic to determine which modes to import. If all is True,
        then all the flags are set to True. If all the flags are True, then all
        is set to True.

        Args:
            flag_all (bool): The value of the all flag.
            flag_salmon (bool): The value of the salmon flag.
            flag_xbattle (bool): The value of the xbattle flag.
            flag_turf (bool): The value of the turf flag.
            flag_anarchy (bool): The value of the anarchy flag.
            flag_private (bool): The value of the private flag.
            flag_challenge (bool): The value of the challenge flag.

        Returns:
            tuple[bool, bool, bool, bool, bool, bool, bool]: The values of the
                flags after the logic has been resolved.
        """
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

        if flag_salmon:
            flag_salmon = False
            self.warn(
                "Salmon Run data is not yet supported. Skipping this mode."
            )

        return (
            flag_all,
            flag_salmon,
            flag_xbattle,
            flag_turf,
            flag_anarchy,
            flag_private,
            flag_challenge,
        )

    def process_data(
        self,
        scraper: SplatNet_Scraper,
        kwargs: dict,
    ) -> list[main.VsExtract]:
        """Retrieves and processes the data from the scraper.

        Args:
            scraper (SplatNet_Scraper): The scraper to get the data from.
            kwargs (dict): The kwargs passed to the run function.

        Returns:
            list[main.VsExtract]: The processed data.
        """
        outs: list[main.VsExtract] = []
        datetime_str = "%Y-%m-%d %H:%M:%S"
        time_str = time.strftime(datetime_str, time.localtime())
        for flag in consts.FLAG_LIST:
            overview, detailed = self.get_matches(
                scraper, time_str, flag, kwargs
            )
            if overview is None:
                continue

            if len(detailed) == 0:
                self.warn(
                    f"No {s.OPTION_COLOR}{consts.FLAG_MAP[flag]}[/] data "
                    "found. Skipping this mode."
                )
                continue

            self.vprint("Processing data...", level=1)
            out = self.process_matches(overview, detailed, flag)
            outs.extend(out)

        return outs

    def get_matches(
        self,
        scraper: SplatNet_Scraper,
        time_str: str,
        flag: consts.FlagType,
        kwargs: dict,
    ) -> tuple[QueryResponse | None, list[QueryResponse]]:
        """Gets the matches from the scraper.

        Args:
            scraper (SplatNet_Scraper): The scraper to get the data from.
            time_str (str): The time string to use for the file names.
            flag (consts.FlagType): The flag to get the data for.
            kwargs (dict): The kwargs passed to the run function.

        Returns:
            tuple[QueryResponse | None, list[QueryResponse]]: The overview and
                detailed data. If the overview is None, then the detailed data
                will be empty. This is intentional.
        """
        if not kwargs.get(flag, False):
            return (None, [])

        message = f"Importing {s.OPTION_COLOR}%s[/] data from SplatNet 3."
        if self.get_from_context("imported") is not None:
            previously_imported = cast(
                list[str], self.get_from_context("imported")
            )
        else:
            previously_imported = []

        previously_imported = cast(list[str], self.get_from_context("imported"))
        with ProgressBar(
            message % consts.FLAG_MAP[flag],
        ) as progress_callback:
            overview, detailed = self.__get_matches(
                scraper,
                flag,
                limit=self.limit,
                progress_callback=progress_callback,
                existing_ids=previously_imported,
            )
        self.save_raw_data(overview, detailed, flag, time_str, kwargs)
        if len(detailed) == 0:
            return (None, detailed)
        return overview, detailed

    def process_matches(
        self,
        overview: QueryResponse,
        detailed: list[QueryResponse],
        flag: consts.FlagType,
    ) -> list[main.VsExtract]:
        """Processes the matches from the scraper.

        Converts the data from the scraper into the data format used by
        data-zipcaster. This will convert the metadata and the matches. If the
        detailed data is empty, then this will return an empty list.

        Args:
            overview (QueryResponse): The overview response from the query.
            detailed (list[QueryResponse]): The detailed responses from the
                query.
            flag (consts.FlagType): The flag that was used to get the data.

        Returns:
            list[main.VsExtract]: The processed data.
        """
        if len(detailed) == 0:
            return []
        out: list[main.VsExtract] = []
        self.vprint("Converting metadata...", level=2)
        metadata = self.convert_metadata(overview, flag)
        self.vprint("Converting matches...", level=2)
        for match in detailed:
            out.append(self.convert_vs_data(match, metadata))
        return out

    def convert_metadata(
        self,
        overview: QueryResponse,
        flag: consts.FlagType,
    ) -> dict[str, main.AnarchyMetadata | main.XMetadata]:
        """Converts the metadata from the scraper.

        Args:
            overview (QueryResponse): The overview response from the query.
            flag (consts.FlagType): The flag that was used to get the data.

        Returns:
            dict[str, main.AnarchyMetadata | main.XMetadata]: The converted
                metadata. This will be empty if the flag is private, turf,
                challenge, or salmon. The key will be the battle ID, and the
                value will be the metadata.
        """
        raw_metadata = splatnet.generate_metadata(overview.data)
        if flag in ("private", "turf", "challenge", "salmon"):
            return {}
        assert isinstance(
            raw_metadata, (splatnet.AnarchyMetadata, splatnet.XMetadata)
        )
        return transforms.convert_metadata(raw_metadata)

    def convert_vs_data(
        self,
        vs_detail: QueryResponse,
        metadata: dict[str, main.AnarchyMetadata | main.XMetadata],
    ) -> main.VsExtract:
        """Converts the vs data from the scraper.

        Args:
            vs_detail (QueryResponse): The detailed response from the query.
            metadata (dict[str, main.AnarchyMetadata  |  main.XMetadata]): The
                metadata for the battle. This will be empty if the flag is
                private, turf, challenge, or salmon. The key will be the battle
                ID, and the value will be the metadata.

        Returns:
            main.VsExtract: The converted vs data.
        """
        vs_detailed = splatnet.generate_vs_detail(vs_detail.data)
        converted_vs = transforms.convert_vs_data(vs_detailed)
        return transforms.append_metadata(converted_vs, metadata)

    def save_raw_data(
        self,
        overview: QueryResponse,
        detailed: list[QueryResponse],
        flag: str,
        time_str: str,
        kwargs: dict,
    ) -> None:
        """Saves the raw data from the query.

        Saves the raw data from the query. This will save the data to the
        directory specified by the save_raw option.

        Args:
            overview (QueryResponse): The overview response from the query.
            detailed (list[QueryResponse]): The detailed responses from the
                query.
            flag (str): The flag that was used to get the data.
            time_str (str): The time string to use for the file names.
            kwargs (dict): The kwargs passed to the run function.
        """
        save_raw = kwargs.get("save_raw", None)
        if save_raw is None or len(detailed) == 0:
            return

        self.vprint(
            f"Saving raw data to {s.EMPHASIZE}{save_raw}[/]...",
            level=1,
        )
        # Check if the path given is absolute or relative
        if not os.path.isabs(save_raw):
            save_raw = os.path.join(os.getcwd(), save_raw)

        base_path = os.path.join(save_raw, time_str, flag)
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Overview
        overview_dict = overview.data
        detailed_dicts = [detailed.data for detailed in detailed]
        overview_path = os.path.join(base_path, "overview.json")
        self.vprint(
            f"Saving overview data to {s.EMPHASIZE}{overview_path}[/]...",
            level=2,
        )
        with open(overview_path, "w") as f:
            json.dump(overview_dict, f)
        self.vprint(
            "Saved overview data!",
            level=3,
        )

        # Detailed
        detailed_path = os.path.join(base_path, "detailed.json")
        self.vprint(
            f"Saving detailed data to {s.EMPHASIZE}{detailed_path}[/]...",
            level=2,
        )
        with open(detailed_path, "w") as f:
            json.dump(detailed_dicts, f)
        self.vprint(
            "Saved detailed data!",
            level=3,
        )

        self.vprint(
            f"Saved raw data to {s.EMPHASIZE}{save_raw}[/]!",
            level=1,
        )

import gzip
import json
import pathlib
import time
from typing import cast

from data_zipcaster.base_plugins import BaseExporter
from data_zipcaster.schemas.vs_modes import VsExtractDict

DEFAULT_OUTPUT_PATH = "Splatoon-3-Battles-%Y-%m-%d-%H-%M-%S.json"


class JSONExporter(BaseExporter):
    @property
    def name(self) -> str:
        return "json"

    @property
    def help(self) -> str:
        return "Exports data to a JSON file.\n\n"

    def get_config_keys(self) -> list[BaseExporter.ConfigKeys]:
        keys = [
            BaseExporter.ConfigKeys(
                key_name="output_path",
                help=(
                    "The path to the output file. If this is not specified, "
                    "the default path is "
                    "[bold yellow]Splatoon-3-Battles-%Y-%m-%d-%H-%M-%S.json[/] "
                    "in the current directory. This key takes precedence over "
                    "all other output path keys."
                ),
                type_=str,
                required=False,
            ),
            BaseExporter.ConfigKeys(
                key_name="output_path_format",
                help=(
                    "The format of the output path. This is formatted using "
                    "Python's strftime format. This key is ignored if "
                    "[bold yellow]output_path[/] is specified."
                ),
                type_=str,
                required=False,
            ),
            BaseExporter.ConfigKeys(
                key_name="output_directory",
                help=(
                    "The directory to output the file to. If this is not "
                    "specified, the current directory is used."
                ),
                type_=str,
                required=False,
            ),
            BaseExporter.ConfigKeys(
                key_name="gzip_output",
                help=(
                    "Whether or not to gzip the output file. If this is not "
                    "specified, the default is [bold yellow]False[/]."
                ),
                type_=bool,
                required=False,
            ),
            BaseExporter.ConfigKeys(
                key_name="json_lines",
                help=(
                    "Whether or not to output the file as JSON Lines. If this "
                    "is not specified, the default is [bold yellow]False[/]."
                ),
                type_=bool,
                required=False,
            ),
        ]
        return keys

    def do_run(self, data: list[VsExtractDict], **kwargs) -> None:
        output_path = self.parse_output_path()
        gzip_output = self.get_from_config(self.name, "gzip_output")
        json_lines = self.get_from_config(self.name, "json_lines")

        if gzip_output:
            if not output_path.endswith(".gz"):
                output_path += ".gz"

        if not json_lines:
            self.to_json(data, output_path, gzip_output=gzip_output)
        else:
            self.to_json_lines(data, output_path, gzip_output=gzip_output)

    def parse_output_path(self) -> str:
        """Parses the output path from the config.

        Returns:
            str: The output path.
        """
        output_path = self.get_from_config(self.name, "output_path")
        output_path_format = self.get_from_config(
            self.name, "output_path_format"
        )

        if output_path and pathlib.Path(output_path).is_absolute():
            return output_path
        elif output_path:
            return pathlib.Path.cwd() / output_path

        current_time = time.gmtime()

        if output_path_format:
            path = self.parse_output_path_format()
            return time.strftime(path, current_time)
        else:
            path = (pathlib.Path.cwd() / DEFAULT_OUTPUT_PATH).as_posix()
            return time.strftime(path, current_time)

    def parse_output_path_format(self) -> str:
        """Parses the output path format from the config.

        Returns:
            str: The output path format.
        """

        # If the output directory was specified in the config, check if it is
        # a full path or a relative path
        if output_directory := self.get_from_config(
            self.name, "output_directory"
        ):
            if pathlib.Path(output_directory).is_absolute():
                path = pathlib.Path(output_directory)
            else:
                path = cast(pathlib.Path, pathlib.Path.cwd() / output_directory)
        else:
            path = pathlib.Path.cwd()

        output_path_format = cast(
            str, self.get_from_config(self.name, "output_path_format")
        )
        return (path / output_path_format).as_posix()

    def to_json(
        self,
        vs_extract_dict: VsExtractDict | list[VsExtractDict],
        file_path: str,
        gzip_output: bool = False,
        **kwargs,
    ) -> None:
        if gzip_output:
            self.__to_json_gzip(vs_extract_dict, file_path, **kwargs)
        else:
            self.__to_json(vs_extract_dict, file_path, **kwargs)

        self.vprint(f"Exported JSON file to {file_path}", level=1)

    def __to_json(
        self,
        vs_extract_dict: VsExtractDict | list[VsExtractDict],
        file_path: str,
        **kwargs,
    ) -> None:
        with open(file_path, "w") as f:
            json.dump(vs_extract_dict, f, **kwargs)

    def __to_json_gzip(
        self,
        vs_extract_dict: VsExtractDict | list[VsExtractDict],
        file_path: str,
        **kwargs,
    ) -> None:
        with gzip.open(file_path, "wt") as f:
            json.dump(vs_extract_dict, f, **kwargs)

    def to_json_lines(
        self,
        vs_extract_dicts: list[VsExtractDict],
        file_path: str,
        gzip_output: bool = False,
        **kwargs,
    ) -> None:
        if gzip_output:
            self.__to_json_lines_gzip(vs_extract_dicts, file_path, **kwargs)
        else:
            self.__to_json_lines(vs_extract_dicts, file_path, **kwargs)

        self.vprint(f"Exported JSON Lines file to {file_path}", level=1)

    def __to_json_lines(
        self,
        vs_extract_dicts: list[VsExtractDict],
        file_path: str,
        **kwargs,
    ) -> None:
        with open(file_path, "w") as f:
            for vs_extract_dict in vs_extract_dicts:
                json.dump(vs_extract_dict, f, **kwargs)
                f.write("\n")

    def __to_json_lines_gzip(
        self,
        vs_extract_dicts: list[VsExtractDict],
        file_path: str,
        **kwargs,
    ) -> None:
        with gzip.open(file_path, "wt") as f:
            for vs_extract_dict in vs_extract_dicts:
                json.dump(vs_extract_dict, f, **kwargs)
                f.write("\n")

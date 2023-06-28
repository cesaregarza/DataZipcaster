import gzip
import json
import pathlib
import time
from typing import cast

import rich_click as click

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

    def do_run(self, data: VsExtractDict, **kwargs) -> None:
        config = self.get_from_context("config")
        output_path = self.parse_output_path()
        gzip_output = config["gzip_output"]
        json_lines = config["json_lines"]

        if gzip_output:
            if not output_path.endswith(".gz"):
                output_path += ".gz"

        if not json_lines:
            self.to_json(data, output_path, gzip_output=gzip_output)
        else:
            self.to_json_lines([data], output_path, gzip_output=gzip_output)

    def parse_output_path(self) -> str:
        """Parses the output path from the config.

        Returns:
            str: The output path.
        """
        config = self.get_from_context("config")
        output_path = config["output_path"]
        output_path_format = config["output_path_format"]

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
        config = self.get_from_context("config")

        # If the output directory was specified in the config, check if it is
        # a full path or a relative path
        if output_directory := config["output_directory"]:
            if pathlib.Path(output_directory).is_absolute():
                path = pathlib.Path(output_directory)
            else:
                path = cast(pathlib.Path, pathlib.Path.cwd() / output_directory)
        else:
            path = pathlib.Path.cwd()

        output_path_format = cast(str, config["output_path_format"])
        return (path / output_path_format).as_posix()

    def to_json(
        self,
        vs_extract_dict: VsExtractDict,
        file_path: str,
        gzip_output: bool = False,
        **kwargs,
    ) -> None:
        if gzip_output:
            self.__to_json_gzip(vs_extract_dict, file_path, **kwargs)
        else:
            self.__to_json(vs_extract_dict, file_path, **kwargs)

        self.vprint(f"Exported JSON file to {file_path}", level=2)

    def __to_json(
        self,
        vs_extract_dict: VsExtractDict,
        file_path: str,
        **kwargs,
    ) -> None:
        with open(file_path, "w") as f:
            json.dump(vs_extract_dict, f, **kwargs)

    def __to_json_gzip(
        self,
        vs_extract_dict: VsExtractDict,
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

        self.vprint(f"Exported JSON Lines file to {file_path}", level=2)

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

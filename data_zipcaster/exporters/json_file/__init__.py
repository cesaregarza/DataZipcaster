import gzip
import json
import logging

from data_zipcaster.schemas.vs_modes import VsExtractDict


class JSONExporter:
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

        logging.info(f"Exported JSON file to {file_path}")

    def __to_json(
        self,
        vs_extract_dict: VsExtractDict,
        file_path: str,
        **kwargs,
    ) -> None:
        with open(file_path, "w") as f:
            json.dump(vs_extract_dict, f, **kwargs)

        logging.info(f"Exported JSON file to {file_path}")

    def __to_json_gzip(
        self,
        vs_extract_dict: VsExtractDict,
        file_path: str,
        **kwargs,
    ) -> None:
        with gzip.open(file_path, "wt") as f:
            json.dump(vs_extract_dict, f, **kwargs)

        logging.info(f"Exported JSON file to {file_path}")

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

        logging.info(f"Exported JSON Lines file to {file_path}")

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

        logging.info(f"Exported JSON Lines file to {file_path}")

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

        logging.info(f"Exported JSON Lines file to {file_path}")

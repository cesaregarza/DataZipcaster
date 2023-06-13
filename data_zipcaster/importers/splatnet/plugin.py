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

    def run(self, *args, **kwargs):
        print("args: ", args)
        print("kwargs: ", kwargs)

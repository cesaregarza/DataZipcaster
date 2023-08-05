Data Zipcaster CLI
==================

The Data Zipcaster CLI is the primary interface for the Data Zipcaster platform. It is a robust, versatile, and easy-to-use command line interface (CLI) for accessing and utilizing the extensive features of the platform.

Usage
-----

The primary command for the CLI is `data_zipcaster`. Currently, the CLI is in an unreleased state and does not have as many quality-of-life features as would be available in the first release. For example, the CLI does not have an automatic updater, and the CLI does not have a PyPI package. These features will be added in the first release.

To get started, use `python data_zipcaster --help` for general help. For specific functionality, try `python data_zipcaster splatnet --help`. The CLI will automatically read and use the configuration file `config.ini` in the root directory of the project. You can also specify a custom configuration file with the `--config` flag followed by the path to the configuration file. The configuration file must follow the INI format, with the following example:

```ini
[splatnet]
session_token = your_session_token
gtoken = your_gtoken
bullet-token = your_bullet_token
monitor-interval = 300
```

Currently the only section names that are supported are for importers and exporters. The values that are accepted are any of the arguments accepted by the importer. Due to limitations with a CLI interface, exporters can only pass their arguments through the config, and cannot be specified on the command line. This is unlikely to change in the future, as it would require much higher complexity argument handling and would be herculean to implement. There is currently no way to show with the CLI what arguments are accepted by an exporter, but this will be added in the first release.

Additionally, all importers support the following flags:

- `--silent`: Disables all output from the importer. Overrides `--verbose`.
- `--verbose`: Enables verbose output from the importer. Is overridden by `--silent`. Short form is `-v`, and stacking is supported for increased verbosity. (e.g. `-vvv`)
- `--config`: Specifies a custom configuration file to use. Default value is `config.ini` in the current working directory.
- `--help`: Shows help for the importer.
- `--monitor`: Enables monitoring mode for the importer. This will cause the importer to run in a loop, checking for new data every `monitor-interval` seconds. If the importer does not support monitoring, this flag will be ignored. This flag will automatically be enabled if the `monitor-interval` is either specified in the config or on the command line.

All options can also be specified in the environment variables. The following order of precedence is used:

1. Command line arguments
2. Environment variables
3. Configuration file
4. Default values

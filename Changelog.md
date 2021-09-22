# Changelog
All notable changes to this project will be documented in this file

[unreleased]: https://github.com/eugenesvk/ListMediaInfo/compare/v2.0@21-1...HEAD
## [Unreleased]
  - __Fixed__
    + :beetle: Error in calculating NFO file name when video stream is missing
    + :beetle: Missing `colon` padding option from the default configuration file

[v2.0@21-1]: https://github.com/eugenesvk/ListMediaInfo/releases/tag/v2.0@21-1
## [v2.0@21-1]
  - __Added__
    + :sparkles: Change config format to [strictyaml](github.com/crdoconnor/strictyaml), make it optional, and expand the list of allowed locations
  - __Fixed__
    + Space separator location

[v1.3@20-6]: https://github.com/eugenesvk/ListMediaInfo/releases/tag/v1.3@20-6
## [v1.3@20-6]
  - __Added__
    + :sparkles: Width adjustment options for A/V format (to make ' AVC'='HEVC', font-specific)
    + `main()` to allow using this as a module
  - __Changed__
    + Regular space to variable width (figure/punctuation/Em depending on context)
    + Paths to __relative__ (when inside `/f1/f2/TV` show just `/TV`)
    + Logging to a separate module
    + Some vars from string to dictionaries for easier parsing

[v1.2@20-4]: https://github.com/eugenesvk/ListMediaInfo/releases/tag/v1.2@20-4
## [v1.2@20-4]
  - __Changed__
    + Update API of PyMediaInfo library to get JSON via the new [Output option](github.com/sbraz/pymediainfo/issues/82)

[v1.1@20-4]: https://github.com/eugenesvk/ListMediaInfo/releases/tag/v1.1@20-4
## [v1.1@20-4]
  - __Changed__
    + Removed non-configurable global vars from config

[v1.0@20-3]: https://github.com/eugenesvk/ListMediaInfo/releases/tag/v1.0@20-3
## [v1.0@20-3]
  - __Added__
    + :sparkles: Auto-generate file name with NFO name from the top folder
    + :sparkles: Calculate padding width based on actual data across __all__ files
    + :sparkles: External config file for key constants
    + Options for less verbose output
    + Options to create a separate NFO file for each sub-folder
  - __Changed__
    + Rework command-line arguments via `argparse`
    + Use [pymediainfo](https://github.com/sbraz/pymediainfo) wrapper to access MediaInfo library instead of the command-line utility

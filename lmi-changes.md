#Changelog
- `v0.2` :sparkles: Can calculate padding width based on actual data across all files
- `v0.3` :sparkles: Auto-generate file name with NFO name from the top folder
- `v0.4` :sparkles: Read key constants from an external config file
- `v0.5` :sparkles: Rework command-line arguments via argparse; added options for less verbose output and to create a separate NFO file for each sub-folder
- `v0.6` :sparkles: use pymediainfo wrapper to access MediaInfo library instead of the command-line utility
- `v1.0` :bookmark: Bump version
- `v1.1` Remove non-configurable global vars from config and minor edits
- `v1.2` Update API of PyMediaInfo library to get JSON via the new Output option (github.com/sbraz/pymediainfo/issues/82)
- `v1.3|20-6`
	+ :sparkles: Add width adjustment options for A/V format (to make ' AVC'='HEVC', font-specific)
	+ Add main() to allow using this as a module
	+ Change regular space to variable width (figure/punctuation/Em depending on context)
	+ Change paths to relative (when inside '/f1/f2/TV' show just '/TV')
	+ Change logging to a separate module
	+ Change some vars from string to dictionaries for easier parsing
- `v2.0@21-1`
	+ :sparkles: Change config format to [strictyaml](github.com/crdoconnor/strictyaml), make it optional, and expand the list of allowed locations
	+ :beetle: Fix space separator location

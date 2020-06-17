#Changelog
- v0.2 feature: can calculate padding width based on actual data across all files
- v0.3 feature: auto-generate file name with NFO name from the top folder
- v0.4 feature: read key constans from an external config file
- v0.5 feature: reworked command-line arguments via argparse; added options for less verbose output and to create a separte NFO file for each sub-folder
- v0.6 feature: use pymediainfo wrapper to access MediaInfo libray instead of the command-line utility
- v1.0 no changes
- v1.1 removed non-configurable global vars from config and minor edits
- v1.2 updated API of PyMediaInfo library to get JSON via the new Output option (github.com/sbraz/pymediainfo/issues/82)
- 1.3@20-6
	+ feature: width adjustment options for A/V format (to make ' AVC'='HEVC', font-specific)
	+ added main() to allow using this as a module
	+ changed regular space to variable width (figure/punctuation/Em depending on context)
	+ changed paths to relative (when inside '/f1/f2/TV' show just '/TV')
	+ changed logging to a separate module
	+ changed some vars from string to dictionaries for easier parsing

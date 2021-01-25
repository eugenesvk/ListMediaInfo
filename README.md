# Overview
__ListMediaInfo__ is a __Python 3__ script that uses [__MediaInfo__](https://mediaarea.net/en/MediaInfo) library to create a list of video files within a folder with key __Video/Audio__ information formatted like this<br>
(three tab-separated columns, space-padded values for vertical alignment):

```
Name	Video                        	Audio&Subs
N1  	 AVC 1920×1080 0.8m  8b      	EAC3 6ch 640k de
N2  	HEVC  704× 468 0.6m 10b crf24	 AAC 2ch  66k +sub, +comment AAC 2ch 66k
```
(the example above is missing tab symbols; actual examples of generated files are in the [__Examples__](./Examples) folder)

__Column Info description__

* __Video__: Format Width×Height BitRate BitDepth RateControlType/Quality<br>
* __Audio&Subs__: _[Track#1]_ Format #ofChannels BitRate Language[if≠en] +Subtitle, _[Track#2+]_ +Title ...

This script also generates a __summary file name__ with the __list/average/range/count of__ values for all the video files within a given folder (depending on the value type/count of unique values).<br>
For example, with the two files listed above the summary file name would have a list of unique values for each info type:<br>
`×Name [AVC-HEVC 468-1080p 0.6-0.8m 8-10b crf24, AAC-EAC3 2-6ch 66-640k +s, +c AAC 2ch 66k, Source]`

...or when there than two unique values, the NFO summary file name would be more varied:<br>
`×Name [AVC-HEVC-MPEG 468–1080p 0.6–17.7m 8-10b abr-crf20-24, AAC-AC3-EAC3 2-6ch 66–640k +s×4, +c×4 AAC 2ch ~63k, Source]`

- show the full list of formats (`AVC-HEVC-MPEG`) or channels (`2-6ch` since only two unique values are present),
- or only a range (min–max) of video heights (`468–1080p`) or bitrates (`0.6–17.7m` or `66–640k`),
- or just the average bitrate (`~63k`, for extra audio tracks),
- or a count of subtitles (`+s×4`):

# Configuration

Key formatting variables used by this script are read from an optional [strictyaml](github.com/crdoconnor/strictyaml) configuration file, which (priority decreasing from left to right):

- can be located at: `~/.config/ListMediaInfo`, OS-default user config path (e.g. `%LocalAppData%\ListMediaInfo` on Windows), `~`, script's location
- can be named as: `lmiconfig.yaml` or `config.yaml` or `.lmiconfig.yaml`

...with defaults set as follows:
```
logMin      : 6             # min logging threshold (1–5, 6+ hides all)
H1          : Name          # Header for Column 1
H2          : Video         # Header for Column 2
H3          : Audio&Subs    # Header for Column 3
pPrefix     : ''            # Prefix symbol for \VideoFolder (blank for os path separator)
NFOPre      : Name [        # NFO file name prefix
NFOSrc      : ', Src'       #               placeholder for source
NFOSuf      : '].nfo'       #               suffix, including extension
jRange      : '–'           # join elements of a numeric list (en-dash '–')
jGen        : '-'           # join elements of a non-numeric list (dash '-')
vDimLimit   : 1.15          # (in NFO file name) use average Height instead of the full range if the values are within this range (e.g. if 480p is only 11%<15% higher than 432p, so file name will have ~456p (average of 432 and 480) instead of 432-480p)
indentlevel : '  '          # log indentation level: '  /Path/2/Folder'
aTMax       : 7             # limit length of Audio title to this # (commentary→comment)
vFpadMin    : 3             # pad Format/Codec name to at least this number of digits
vWpadMin    : 3             # ... Width ...
vHpadMin    : 3             # ... Height ...
vBRpadMin   : 3             # ... video Bit Rate ...
vBDpadMin   : 1             # ... video Bit Depth ...
aFpadMin    : 3             # ... audio Format/Codec name ...
aBRpadMin   : 3             # ... audio Bit Rate (first track)...
padFormat   : Y             #Y/N Adjust different widths to vertically align. This is font-specific and might mess up alignment in fixed-width editors
Font        : Cambria     # default font
padFmt      :
  Cambria   :
    AVC     : '      AVC'       # = 'HEVC'
    AAC     : ' AAC'        # = 'EAC3'
    AC3     : '   AC3'        # = 'EAC3'
    m       : '     '          # = 'm'
```

# Requirements

1. [__MediaInfo__](https://mediaarea.net/en/MediaInfo) library (on Windows and macOS this should be bundled within the `pymediainfo` Python module and as a result not needed to be installed separately)

2. __Text Editor__: [elastic tabstop](nickgravgaard.com/elastic-tabstops/) package to see tab-separated columns as vertically aligned

3. __Python 3 Modules__:
```
pip install natsort fastnumbers PyICU
pip install pymediainfo             	# wrapper to access MediaInfo library
pip install -e "/path/to/hfilesize/"	# get from github.com/eugenesvk/hfilesize (it has an extra 'css' style without space and the useless 'b' indicator)
OR                                  	# when/if [PR](github.com/simonzack/hfilesize/pull/4) is merged
pip install hfilesize
pip install AppDirs
pip install strictyaml
```

# Command Line flags
__usage__:

* ListMediaInfo.py [-h] [-e] [-s] [-v] InputPath [OutputName]

__positional arguments__:

* `InputPath`      Add /Path/To/Input/Video (or ‘.’ for current folder)
* `OutputName`     Output file name [default=“/”: generate from files in the current folder]

__optional arguments__:

* `-e, --each`     create one NFO file for each (sub)folder instead of one for all (sub)folders
* `-s, --silent`   hide list of processed files

__optional info arguments__:

*  `-h, --help`     show help message and exit
*  `-v, --version`  show program's version number and exit

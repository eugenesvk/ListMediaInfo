#!/usr/bin/env python3
# Set global variables
debug      	= 0           	# 5 levels of verbosity
H1         	= 'Name'      	# Header for Column 1
H2         	= 'Video'     	# Header for Column 2
H3         	= 'Audio&Subs'	# Header for Column 3
fPrefix    	= '×'         	# Prefix symbol for ×/path/to/folder/
NFOPre     	= '×Name ['   	# NFO file name prefix
NFOSrc     	= ', Source'  	#               placeholder for source
NFOSuf     	= '].nfo'     	#               suffix, including extension
jRange     	= '–'         	# join elements of a numeric list (en-dash '–')
jGen       	= '-'         	# join elements of a non-numeric list (dash '-')
vDimLimit  	= 1.15        	# (in NFO file name) use average Height instead of the full range if the values are within this range (e.g. if 480p is only 11%<15% higher than 432p, so file name will have ~456p (average of 432 and 480) instead of 432-480p)
indentlevel	= '  '        	# log indentation level: '  /Path/2/Folder'
aTMax      	= 7           	# limit length of Audio title to this # (commentary→comment)
padFill    	= ' '         	# filler symbol for padding (use visible '°' for testing)
vFpadMin   	= 3           	# pad Format/Codec name to at least this number of digits
vWpadMin   	= 3           	# ... Width ...
vHpadMin   	= 3           	# ... Height ...
vBRpadMin  	= 3           	# ... video Bit Rate ...
vBDpadMin  	= 1           	# ... video Bit Depth ...
aFpadMin   	= 3           	# ... audio Format/Codec name ...
aBRpadMin  	= 3           	# ... audio Bit Rate (first track)...
extensions 	= ['.MP4','.AVI','.MOV','.M4V','.VOB','.MPG','.MPEG',\
           	   '.MKV','.WMV','.ASF','.FLV','.RM','.OGM','.M2TS','.RMVB']

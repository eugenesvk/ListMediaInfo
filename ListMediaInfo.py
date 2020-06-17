#!/usr/bin/env python3

import sys, os
from os import listdir
from os.path import isfile, join
import subprocess
import json
import re
from collections import defaultdict as ddict # allows autocreation of empty keys
import argparse
from argparse import RawDescriptionHelpFormatter as RawDHF, RawTextHelpFormatter
from pymediainfo import MediaInfo as wrapMI
from hfilesize import Format, FileSize
from natsort import natsorted, humansorted, ns
import logging
from logging import log as log
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

from lmiconfig import * # import global vars from an external config
logging.basicConfig(format='%(levelname)s: %(message)s', level=logMin)

recDD = lambda: ddict(recDD) # recursive dicts, allows x['a']['b']['c']['d'] w/o KeyError

def setGlobals(): # Set global variables
  global NFOname0,vSource,vDict,vfDict,vDictCol,writeBuffer,level,padF,args, pPrefix
  NFOname0   	= ''          	# (empty) NFO file name for the top folder
  vSource    	= '.'         	# (redundant?) Default path — current folder
  vDict      	= ddict(list) 	# Stores selected file info to generate folder.nfo
  vfDict     	= {}          	# Stores all file info ~{'fIndex': {'fCat1':fCat1,...}}
  vDictCol   	= recDD()     	# Stores formatted file info for A/V columns
  writeBuffer	= []          	# Buffer to write .nfo data to instead of directly to file
  level      	= 0           	# Folder level
  padF       	= padFmt[Font]	# width diff 'HE' vs 'A' @Font: .replace(' AVC',padF['AVC'])
  args       	= argparse.ArgumentParser() # Empty argparse object
  pPrefix    	= pPrefix if pPrefix>'' else os.sep # Path separator

def files(path):
  for item in os.listdir(path):
    if os.path.isfile(os.path.join(path, item)):
      yield item
def filesorted(path):
  files = [f for f in listdir(path) if isfile(join(path, f))]
  filesrt = humansorted(files) #natsorted
  for item in filesrt:
    yield item
def folders(path):
  for item in os.listdir(path):
    if os.path.isdir(os.path.join(path, item)):
      yield item
def unique(ilist): # function to get unique values
  list_set   	= set(ilist)      	# insert the list to the set
  unique_list	= (list(list_set))	# convert the set to the list
  return unique_list
def resetVarList(): #reset global varibles for each new folder
  global vfDict,vDict,vDictCol
  vfDict, vDictCol, vDict	= ({}, recDD(), ddict(list))
  global vFpad,vWpad,vHpad,vBRpad,vBDpad,aFpad,aBRpad
  vFpad,vWpad,vHpad,vBRpad,vBDpad,aFpad,aBRpad = (vFpadMin,vWpadMin,vHpadMin,vBRpadMin,vBDpadMin,aFpadMin,aBRpadMin)

def getNFOname(vFolder):
  global vDict
  log(3,"NFO: vDict before reset:" + str(vDict))

  #Video:  FileName.nfo vF vW×vH vBR vBD'b'+vRC (all values are ranges for all listed files)
  # vF,vW,vH,vBD,vBR,vrcType,vrcValue,FileName = ('','','','','','','','')
  # List of unique/min-max(str→int) values with a jGen(dash)/jRange(em-dash) separator
  vFunique = unique(vDict['vF'])
  vFunique.sort() #sort list in place
  vF	= jGen.join(map(str,vFunique))
  FileName       	= ddict(str) # empty dictionary to collect NFO file name
  FileName['vF'] 	= str(vF)
  FileName['Out']	= FileName['vF'] # store intermediate results here (cumulatively)
  log(3,'FileName+vF: ' + FileName['Out'])

  vW    	= list(map(int,(unique(vDict['vW']))))	#Unique list of Widths, →int for sorting
  vH    	= list(map(int,(unique(vDict['vH']))))	#Unique list of Heights, →int for sorting
  vHFull	= list(map(int,vDict['vH']))          	#Full list of Heights, →int for sorting
  vWxH  	= [str(a)+'×'+str(b) for a,b in zip(vW,vH)] #string
  vHmin 	= min(vH); vHmax = max(vH); vHavg = int(sum(vHFull)/float(len(vHFull)))
  if (len(vWxH)==1):
    FileName += ' '+vWxH[0]
  elif (len(vWxH)>1):
  log(3, "vDict['vW/vH']→unique values→integers")
  log(3, '\tvW:'+str(vDict['vW']) +'\t→ '+str(unique(vDict['vW']))+'\t→ '+str(vW))
  log(3, '\tvH:'+str(vDict['vH']) +'\t→ '+str(unique(vDict['vH']))+'\t→ '+str(vH))
  log(3, 'vWxH text: '+str(vWxH)+', lenght: '+str(len(vWxH))+', vWxH[0]: '+str(vWxH[0]))
  log(3, 'vHmin: '+str(vHmin)+', vHmax: '+str(vHmax))
    if (int(vHmax)/int(vHmin)>vDimLimit):
      if (len(vHFull)==2):
        FileName += ' '+str(vHmin)+jGen+str(vHmax)+'p'
      elif (len(vHFull)>2):
        FileName += ' '+str(vHmin)+jRange+str(vHmax)+'p'
    else:
      FileName += ' ~'+str(vHavg)+'p'
  if debug>2: print('Debug getNFOname, FileName+vWxH: ' + str(FileName))
  log(3,'FileName+vDim: ' + FileName['Out'])

  vBR    	= list(map(int,(unique(vDict['vBR'])))) #Unique list of BitRates, →int for sorting
  vBRFull	= list(map(int,vDict['vBR']))           #Full list of BitRates
  if vBR!=[]:
    vBRmin	='{:.1fhcss^2}'.format(FileSize(min(vBR))) #1234567 → 1.2m
    vBRmax	='{:.1fhcss^2}'.format(FileSize(max(vBR)))
    if (len(vBRFull)==1):
      FileName += ' '+vBRmin
    elif (len(vBRFull)==2):
      FileName += ' '+vBRmin.replace('m','')+jGen+vBRmax
    elif (len(vBRFull)>2):
      FileName += ' '+vBRmin.replace('m','')+jRange+vBRmax
  log(3, "vDict['vBR']→unique values→integers")
  log(3, '\tvBR:'+str(vDict['vBR']) +'\t→ '+str(unique(vDict['vBR']))+'\t→ '+str(vBR))
  log(3, 'FileName+vBR: ' + FileName['Out'])

  vBD     	= vDict['vBD']
  vrcType 	= vDict['vrcType']
  vrcValue	= vDict['vrcValue']
  vBD     	= list(map(int,(unique(vBD))))
  vrcType 	= list(map(str,(unique(vrcType))))
  vrcValue	= list(map(float,(unique(vrcValue))))
  vBD.sort()
  vrcType.sort()
  vrcValue.sort()
  vBD     	= jGen.join(str(i) for i in vBD)
  vrcType 	= jGen.join(str(i) for i in vrcType)
  vrcValue	= jGen.join(str(i).replace('.0','') for i in vrcValue)
  vBDSep = ''
  if len(vrcType+vrcValue)>0: vBDSep=' '
  FileName += ' '+vBD+'b'+vBDSep+vrcType+vrcValue
  log(3, 'Uniqe, sorted & -joined:')
  log(3, '...vBD     \t: ' + vBD)
  log(3, '...vrcType \t: ' + vrcType)
  log(3, '...vrcValue\t: ' + vrcValue)

  #Audio: aStart aF aCh'ch' aBR (values are ranges for all listed files)
  aF,aCh,aBR,aLang = (vDict['aF'],vDict['aCh'],vDict['aBR'],vDict['aLang'])
  tSubLen = len(vDict['tSub'])	# number of files with subtitles
  tSubI,aLangI = ('','')      	# empty subtitle/language indicator
  if tSubLen==1: tSubI = ' +s'	# make sub indicator visible
  if tSubLen>1: tSubI = ' +s' + '×' + str(tSubLen)
  if (len(unique(aLang))==1 and len(aLang[0])>0 and aLang[0]!='en'): #if all languages are the same, have a label, but not 'en'
    aLangI = ' ' +aLang[0]      #   make lang indicator visible

  # List of unique/min-max(str→int) values with a jGen(dash)/jRange(em-dash) separator
  aFunique = unique(aF)
  aFunique.sort() #sort list in place
  aF	= jGen.join(map(str,aFunique))
  FileName = FileName + ', '+str(aF)
  log(3,'getNFOname: Unique aF\t: ' + str(aF))
  log(3,'FileName[aF]: ' + FileName['aF'])

  aCh	= list(map(int,(unique(aCh)))) #converted to int for sorting
  if aCh!=[]:
    aChmin	= str(min(aCh))
    aChmax	= str(max(aCh))
    if (len(aCh)==1):
      FileName += ' '+aChmin+'ch'
    elif (len(aCh)==2):
      FileName += ' '+aChmin+jGen+aChmax+'ch'
    elif (len(aCh)>2):
      FileName += ' '+aChmin+jRange+aChmax+'ch'

  aBR	= list(map(int,(unique(aBR)))) #converted to int for sorting
  if aBR!=[]:
    aBRmin	='{:.0fhcss^1}'.format(FileSize(min(aBR))) #123456 → 123k
    aBRmax	='{:.0fhcss^1}'.format(FileSize(max(aBR)))
    if (len(aBR)==1):
      FileName += ' '+aBRmin
    elif (len(aBR)==2):
      FileName += ' '+aBRmin.replace('k','')+jGen+aBRmax
    elif (len(aBR)>2):
      FileName += ' '+aBRmin.replace('k','')+jRange+aBRmax
  FileName += aLangI+tSubI
  log(3, "vDict['aBR']→unique values→integers")
  log(3, '\taBR:'+str(vDict['aBR']) +'\t→ '+str(unique(vDict['aBR']))+'\t→ '+str(aBR))
  log(3, 'FileName+aF+aCh+aBR: ' + FileName['Out'])

  # Extra Commentary audTracks: list of unique/avg(str→int) values with a jGen(dash) separator
  aF1,aCh1,aBR1,aLang1,aT1 = (vDict['aF1'],vDict['aCh1'],vDict['aBR1'],vDict['aLang1'],vDict['aT1'])
  aF1swap,aCh1swap,aBR1swap = ([],[],[]) #temporay swap list
  aComCount = 0
  for i in range(len(aF1)): #leave only extra tracks with title starting with 'Commentary'
    if aT1[i].startswith('Commentary'):
      aComCount += 1
      aF1swap.append(aF1[i])
      aCh1swap.append(aCh1[i])
      aBR1swap.append(aBR1[i])
  #remove all non-commentary tracks
  aF1=aF1swap
  aCh1=aCh1swap
  aBR1=aBR1swap

  # aF1len = len(aF1)
  if aComCount==0:
    FileName += NFOSrc
    return FileName                                	#return if no extra commentary tracks
  if aComCount>1: aComCountI = '×' + str(aComCount)	#add No of commentary tracks if >1
  else: aComCountI = ''
  aF1unique = unique(aF1)
  aF1unique.sort() #sort list in place
  aF1    = jGen.join(map(str,aF1unique))
  FileName = FileName + ', +c'+aComCountI+' '+str(aF1)
  log(3,'getNFOname: Unique aF1\t: ' + str(aF1))
  log(3,'getNFOname +aF1: ' + FileName['Out'])

  aCh1   	= list(map(int,(unique(aCh1)))) #unique channel#, converted to int for sorting
  aCh1min	= str(min(aCh1))
  aCh1max	= str(max(aCh1))
  aCh1len	= len(aCh1)
  if (aCh1len==1):
    FileName += ' '+aCh1min+'ch'
  elif (aCh1len==2):
    FileName += ' '+aCh1min+jGen+aCh1max+'ch'
  elif (aCh1len>2):
    FileName += ' '+aCh1min+jRange+aCh1max+'ch'
  log(3,'getNFOname +aCh1: ' + FileName['Out'])

  aBR1List 	= list(map(int,aBR1)) #non-unique bitrate#, converted to int for averaging
  aBR1     	= list(map(int,(unique(aBR1)))) #unique bitrate#, converted to int for sorting
  # aBR1avg	= int(sum(aBR1)/float(len(aBR1)))
  aBR1avg  	= int(sum(aBR1List)/float(len(aBR1List))) 	#average based on full list
  aBR1avg  	= '{:.0fhcss^1}'.format(FileSize(aBR1avg))	#123456 → 123k
  aBR1len  	= len(aBR1)
  if (aBR1len==1):
    FileName += ' '+aBR1avg
  elif (aBR1len>1):
    FileName += ' ~'+aBR1avg
  FileName += NFOSrc
  if debug>1: print('Debug getNFOname with Audio2: ' + str(FileName))
  log(3, "vDict['aBR1']→unique values→integers")
  log(3, '\taBR1:'+str(vDict['aBR1']) +'\t→ '+str(unique(vDict['aBR1']))+'\t→ '+str(aBR1))
  log(3, 'FileName+BitRate: ' + FileName['Out'])

  return FileName

def getMediaInfo(mediafile): #pymediainfo import MediaInfo as wrapMI
  MIJSON = wrapMI.parse(mediafile, output="JSON")
  data = json.loads(MIJSON) #Decode JSON: Deserialize stdout to a Python object (object→dict)
  return data

def formatvStreamInfo(i, vStream):
  global vDict
  vt = vStream
  vF,vW,vH,vBD = (vt['Format'],vt['Width'],vt['Height'],vt['BitDepth'])
  try: #MPEG-4 Video → MPEG
    vF = re.search('\\w*(?= )', vF.replace('-','')).group(0)
  except:
    pass
  try:
    vBR = vt['BitRate']
    vDict['vBR'].append(vBR)
    vBR ='{:.1fhcss^2}'.format(FileSize(vBR)) #1234567 → 1.2m
  except:
    vBR = '    ' #space equivalent of '1.2m'
  try:
    vEnc = (vt['Encoded_Library_Settings'])
  except:
    vEnc = ''
  vDict['vF'].append(vF)
  vDict['vW'].append(vW)
  vDict['vH'].append(vH)
  vDict['vBD'].append(vBD)
  vF = '{msg:{fill}{align}{width}}'.format(msg=vF,fill=padFill,align='>',width=vFpad)
  vW = '{msg:{fill}{align}{width}}'.format(msg=vW,fill=padFill,align='>',width=vWpad)
  vH = '{msg:{fill}{align}{width}}'.format(msg=vH,fill=padFill,align='>',width=vHpad)
  vBD = '{msg:{fill}{align}{width}}'.format(msg=vBD,fill=padFill,align='>',width=vBDpad)
  vBR = '{msg:{fill}{align}{width}}'.format(msg=vBR,fill=padFill,align='>',width=vBRpad)
  if debug>4: print('vEnc \t= {' + vEnc +'}')
  if i>0:	vEnd = ', '
  else:  	vEnd = '\t'
  try: #type of rate control after 'rc=', e.g. 'crf' or '2 / pass'
    vrcType = re.search('(?<=rc=)(([a-z.]+)|(2 / pass)|(2pass))(?= / )', vEnc).group(0)
    vrcType = re.sub(' / ', '', vrcType) #remove ' / ' from '2 / pass'
    vDict['vrcType'].append(vrcType)
  except:
    vrcType = ''
  try: #value of rate control after 'crf='
    vrcValue = re.search('(?<=/ crf=)[0-9.]+(?= / )', vEnc).group(0)
    vrcValue = str(float(vrcValue)).replace('.0','') #remove extra trailing zeroes
    vDict['vrcValue'].append(vrcValue)
  except:
    vrcValue = ''
  vRC = ' ' + vrcType + vrcValue
  if vRC==' ': vRC=''

  data = '\t'+vF+' '+vW+'×'+vH+' '+str(vBR)+' '+vBD+'b'+vRC+vEnd
  return data #Codec Width×Height BitRate BitDepth

def formataStreamInfo(i, aStream, tSub): #parse Audio Stream info
  global vDict
  at = aStream
  log(1,at)
  Fpad,BRpad = (aFpad,aBRpad)
  aF,aCh,aBR,aLang,aT = (at['Format'],at['Channels'],'','','')
  try:
    aBR = at['BitRate']
  except:
    aBR = 0
  try:
    aLang = at['Language']
  except:
    pass
  try:
    aT = at['Title']
  except:
    pass
  aF = aF.replace('-','') #E-AC3→EAC3
  if i==0:
    vDict['aF'].append(aF)
    vDict['aCh'].append(aCh)
    vDict['aBR'].append(aBR)
    vDict['aLang'].append(aLang)
  else:
    vDict['aF1'].append(aF)
    vDict['aCh1'].append(aCh)
    vDict['aBR1'].append(aBR)
    vDict['aLang1'].append(aLang)
    vDict['aT1'].append(aT)
    Fpad,BRpad = (0,0)	# Don't pad Format/Bitrate for second+ streams
  aF = '{msg:{fill}{align}{width}}'.format(msg=aF,fill=padFill,align='>',width=Fpad)
  aBR ='{:.0fhcss^1}'.format(FileSize(aBR)) #123456 → 123k
  aBR = '{msg:{fill}{align}{width}}'.format(msg=aBR,fill=padFill,align='>',width=BRpad)
  aStart,aEnd,aLangI = ('','','')
  if i>0  : aStart = ', +' + aT[:aTMax].lower()+' '	# Limit Title length→lower case
  if i==0 : aEnd = tSub                            	# mark 1st aud stream as having a subtitle
  if aLang!='en': aLangI = ' ' +aLang              	# add language indicator unless 'en'

  data = aStart+aF+' '+aCh+'ch'+' '+str(aBR)+aLangI+aEnd
  # log(4,'data \t= {' + data +'}')
  return data #[, +Title] Codec Channels BitRate +Subtiles (e.g. 'AAC 6ch 192k +sub' or ', +comment AAC 2ch 60k'

def storeFileInfo(vFolder,file,level,fi): #Store info for a video file in a global dictionary
  # Initialize
  global vfDict
  vStreams,aStreams,tStreams = ([],[],[])
  vFile = vFolder + file
  fvbase = os.path.basename(vFile)
  fvname = os.path.splitext(fvbase)[0]
  log(2,'storeFileInfo(' + vFolder +', ' + ', ' + file + ')')
  spacer = indentlevel*level
  if not args.silent: print(spacer+' '+vFile) # list

  # Get MediaInfo as a JSON object (=Python dictionary) and extract media tracks
  MI      	= getMediaInfo(vFile)
  MITracks	= MI['media']['track']

  # Split MediaInfo data into separate Vid/Aud/Text streams
  for i in range(len(MITracks)): #Create list of video/audio/text stream
    track = MITracks[i]
    if (track['@type'] == 'Video'):
      vStreams.append(track)
    elif (track['@type'] == 'Audio'):
      aStreams.append(track)
    elif (track['@type'] == 'Text'):
      tStreams.append(track)

  if len(tStreams)>0:
    tSub = ' +sub' # Test if subtitles exist
    vDict['tSub'].append(tSub)
  else:	tSub = ''

  # Store all the information in a file dictionary under the key 'file index'
  vfDict.update({fi: {'fvname':fvname,'vStreams':vStreams,'aStreams':aStreams,'tStreams':tStreams,'tSub':tSub}})

def writeFileInfo(fi): #Read video file info from a global dictionary and write it to NFO
  global vfDict,writeBuffer
  fvname = vfDict[fi]['fvname']
  vStreams = vfDict[fi]['vStreams']
  aStreams = vfDict[fi]['aStreams']
  tStreams = vfDict[fi]['tStreams']
  tSub = vfDict[fi]['tSub']

  # Parse each Vid/Aud/Sub stream and write selected stream output to file
  writeBuffer.append(fvname) #1. File name

  for i in range(len(vStreams)): # Create list data for each Video stream
    vInfo = formatvStreamInfo(i,vStreams[i])
    writeBuffer.append(vInfo) #2. Video info

  for i in range(len(aStreams)): # Create list data for each Audio stream
    aInfo = formataStreamInfo(i,aStreams[i],tSub)
    writeBuffer.append(aInfo) #3. Audio info

  writeBuffer.append('\n') #4. New line

  log(1,'vStreams∑=' + str(len(vStreams)) + ':' + str(vStreams) + '\n')
  log(1,'aStreams∑=' + str(len(aStreams)) + ':' + str(aStreams) + '\n')
  log(1,'tStreams∑=' + str(len(tStreams)) + ':' + str(tStreams) + '\n')

def setPadValues(filesNo): #set padding values to match the max value in range
  global vFpad,vWpad,vHpad,vBDpad,vBRpad,aFpad,aBRpad,vfDict
  vStreams,aStreams,aBR=([],[],'')
  for fi in range(filesNo): #get aud/video stream data for each file
    vStreams = vfDict[fi]['vStreams']
    aStreams = vfDict[fi]['aStreams']
    for j in range(len(vStreams)): # for each stream, get max length of var to pad to
      log(1,'fvname,fi,j'+"|"+vfDict[fi]['fvname']+"|"+str(fi)+"|"+str(j))
      try:
        vt	= vStreams[j]
        vF,vW,vH,vBD = (vt['Format'],vt['Width'],vt['Height'],vt['BitDepth'])
        try: #MPEG-4 Video → MPEG
          vF = re.search('\\w*(?= )', vF.replace('-','')).group(0)
        except:
          pass
        vFpad 	= max(vFpad 	, len(vF))
        vWpad 	= max(vWpad 	, len(vW))
        vHpad 	= max(vHpad 	, len(vH))
        vBDpad	= max(vBDpad	, len(vBD))
        vBR   	='{:.1fhcss^2}'.format(FileSize(vt['BitRate'])) #1234567 → 1.2m
        vBRpad	= max(vBRpad, len(vBR))
      except:
        pass
      try:
        at    	= aStreams[j]
        aF    	= at['Format'].replace('-','')
        aFpad 	= max(aFpad, len(aF))
        aBR   	='{:.0fhcss^1}'.format(FileSize(at['BitRate'])) #123456 → 123k
        aBRpad	= max(aBRpad, len(aBR))
      except:
        pass
  log(3,'vFpad(3)='+str(vFpad) + '|vWpad(3)='+str(vWpad) + '|vHpad(3)='+str(vHpad) + '|vBDpad(1)='+str(vBDpad) + '|vBRpad(3)='+str(vBRpad) + '|aFpad(3)='+str(aFpad) + '|aBRpad(3)='+str(aBRpad))

def LoopFiles(vFolder='.',level=1,each=False): # call FileInfo for videos and self on subfolders
  global writeBuffer,NFOname0
  level += 1
  spacer = indentlevel*level
  log(5,spacer + '[' + vFolder)

  if os.path.isdir(vFolder):
    if vFolder[-1] != "/": vFolder += "/"
    resetVarList() #reset global variables to empty/defaults for each new folder
    filesNo = 0

    for file in filesorted(vFolder):
      ext = os.path.splitext(file)[1]
      if ext.upper() in extensions:
        storeFileInfo(vFolder, file, level, filesNo) #Store file info in a global dictionary
        filesNo += 1
      elif not(ext.upper() == '.JPG' or ext.upper() == '.TXT'):
        log(5,spacer + '→' + vFolder + file)

    if filesNo==0:
      log(5,'No video files in this folder: ' + vFolder)
    else:
      Header = H1+'\t'+H2+'\t'+H3+'\n'
      writeBuffer.append(fPrefix + vFolder + '\n' + Header) #Folder header info
      setPadValues(filesNo)
      for i in range(filesNo): writeFileInfo(i)
      NFOname = getNFOname(vFolder)
      log(2, nfo['vF'] +' '+ nfo['vDim'] +' '+ nfo['vBR'] +' '+ nfo['vBD']+' '+ nfo['vRC'] +', '+ nfo['aF'] +' '+ nfo['aCh'] +' '+ nfo['aBR'] +' '+ nfo['Lang']+' '+ nfo['Sub'] + nfo['aF1'] +' '+ nfo['aCh1'] +' '+ nfo['aBR1'])
      if level==1: NFOname0 = NFOname
      writeBuffer.append('———NFO[' + NFOname + ']\n\n')
      if each:
        target=vFolder+NFOPre + NFOname + NFOSuf #
        writeBufferToFile(target)
        pass

    for folder in folders(vFolder):
      LoopFiles(vFolder+folder,level,each)
  if debug>0: print(spacer+' '+ vFolder +  ']')
  level = level - 1

def writeBufferToFile(target): # write writeBuffer to file and reset it
  global writeBuffer

  if os.path.isfile(target):
    overwrite = input(target + ' already exists. Overwrite?\n"x" to Exit; Anything else but "y" is a no: ')
    if overwrite.lower() == 'x':
      print('✗\nExiting to avoid overwriting an existing file: ' + target)
      sys.exit()
    elif overwrite.lower() != 'y':
      print('✗\nSkipping to avoid overwriting an existing file: ' + target)
      writeBuffer=[]
      return

  #w+ Opens a file for writing+reading, overwrites existing/create new
  fOut = open(target,'w+',encoding='utf-8')
  for item in writeBuffer:
    fOut.write(f'{item}')
  fOut.close

  print('\n✓\n' + target)
  if logMin<6:
    fOut = open(target,'r')
    if fOut.mode == 'r': log(5,fOut.read())
    fOut.close

  writeBuffer=[]

def main():
  parser = argparse.ArgumentParser(description="Create a list of video files with key Vid/Aud info formatted like this\n(tab-separted columns, space-padded values for vertical alignment):\n"+"  "+H1+"\t"+H2+"                       \t"+H3+"""
    N1\t AVC 1920×1080 0.8m  8b      \tEAC3 6ch 640k de
    N2\tHEVC  704× 468 0.6m 10b crf24\t AAC 2ch  66k +sub, +comment AAC 2ch 66k

  where
    Vid\tFormat Width×Height Bitrate Bitdepth RateControl Type/Quality
    Aud\t[Track#1] Format #ofChannels Bitrate Language≠en +Subtitle, [Track#2+] +Title ...

  ...and a summary NFO file name with the list/count/average/range of values:\n  """+NFOPre+"AVC-HEVC 468-1080p 0.6-0.8m 8-10b crf24, AAC-EAC3 2-6ch 66-640k +s, +c AAC 2ch 66k"+NFOSrc+NFOSuf, formatter_class=RawDHF)
  group = parser.add_mutually_exclusive_group()
  parser.add_argument("input"         , metavar="InputPath", help="Add /Path/To/Input/Video (or '.' for current folder)")
  group.add_argument("-e","--each"    , action="store_true", help="create one NFO file for each (sub)folder instead of one for all (sub)folders")
  parser.add_argument("-s","--silent" , action="store_true", help="hide list of processed files")
  group.add_argument("out"            , nargs='?',default="/", metavar="OutputName", help='Output file name [default="/": generate from files in the current folder]')
  groupI = parser.add_argument_group('optional info arguments')
  groupI.add_argument('-v','--version'  , action='version', version='%(prog)s 1.2@20-4')
  global args
  args = parser.parse_args()
  # group.add_argument("-o","--out" , nargs='?',const="×Output", metavar="Name", help='Output file name [default: "×Output"; no flag: generated from files in the current folder]')
  log(2,args) #print command line ArgumentParser

  vSource = os.path.normpath(args.input)
  if vSource[-1] != '/': vSource += '/'
  log(4, '▶vSource : ' + vSource)

  #Create a global dictionary with all a/v info for all a/v files recursively
  LoopFiles(vSource,level,args.each) # if -e also writes to file in each folder

  if args.out!='/': # use OutputName when it's given ('/' is the value when empty)
    target = os.path.normpath(vSource+args.out) # (Win) converts / to \
    targetInfo = ' (user input)'
  else: # Default to auto-generated NFO file name based on the initial folder (unless -e)
    target = os.path.normpath(vSource+NFOPre + NFOname0 + NFOSuf)
    targetInfo = ' (auto-generated)'

  log(5,'\n"ListMediaInfo.py ' + vSource + ' ' + target+'"'+targetInfo)

  if not args.each: writeBufferToFile(target) # if not -e write to one file for all folders

if __name__ == '__main__':
  main()

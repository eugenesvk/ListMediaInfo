#!/usr/bin/env python3

import sys, os
from os import listdir
from os.path import isfile, join
import subprocess
import json
import re
import argparse
from argparse import RawDescriptionHelpFormatter as RawDHF, RawTextHelpFormatter
from pymediainfo import MediaInfo as wrapMI
from hfilesize import Format, FileSize
from natsort import natsorted, humansorted, ns
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Import global variables from an external config
from lmiconfig import debug,level,fPrefix,NFOname0,NFOPre,NFOSrc,NFOSuf,vSource,H1,H2,H3,vDict,vfDict,writeBuffer,jRange,jGen,indentlevel,vDimLimit,aTMax,vFpadMin,vWpadMin,vHpadMin,vBRpadMin,vBDpadMin,aFpadMin,aBRpadMin,padFill,extensions

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
  global vfDict,vDict
  vfDict = {}
  vDict	= {'vF':[],'vW':[],'vH':[],'vWxH':[],'vBR':[],'vBD':[],'vrcType':[],'vrcValue':[],
           'aF':[], 'aCh':[], 'aBR':[], 'aLang':[],
           'aF1':[],'aCh1':[],'aBR1':[],'aLang1':[],'aT1':[],
           'tSub':[]} # vDict['key'].append('1')
  global vFpad,vWpad,vHpad,vBRpad,vBDpad,aFpad,aBRpad
  vFpad,vWpad,vHpad,vBRpad,vBDpad,aFpad,aBRpad = (vFpadMin,vWpadMin,vHpadMin,vBRpadMin,vBDpadMin,aFpadMin,aBRpadMin)

def getNFOname(vFolder):
  global vDict
  if debug>2: print("Debug getNFOname: vDict before reset:" + str(vDict))

  #Video:  FileName.nfo vF vW×vH vBR vBD'b'+vRC (all values are ranges for all listed files)
  # vF,vW,vH,vBD,vBR,vrcType,vrcValue,FileName = ('','','','','','','','')
  # List of unique/min-max(str→int) values with a jGen(dash)/jRange(em-dash) separator
  vFunique = unique(vDict['vF'])
  vFunique.sort() #sort list in place
  vF	= jGen.join(map(str,vFunique))
  if debug>2: print('Debug getNFOname: Unique vF\t: ' + str(vF))
  FileName = str(vF)
  if debug>2: print('Debug getNFOname, FileName+vF: ' + str(FileName))

  vW    	= list(map(int,(unique(vDict['vW']))))	#Unique list of Widths, →int for sorting
  vH    	= list(map(int,(unique(vDict['vH']))))	#Unique list of Heights, →int for sorting
  vHFull	= list(map(int,vDict['vH']))          	#Full list of Heights, →int for sorting
  vWxH  	= [str(a)+'×'+str(b) for a,b in zip(vW,vH)] #string
  vHmin 	= min(vH); vHmax = max(vH); vHavg = int(sum(vHFull)/float(len(vHFull)))
  if debug>2:
    print("vDict['vW/vH']→unique values→integers")
    print('\tvW:'+str(vDict['vW']) +'\t→ '+str(unique(vDict['vW']))+'\t→ '+str(vW))
    print('\tvH:'+str(vDict['vH']) +'\t→ '+str(unique(vDict['vH']))+'\t→ '+str(vH))
    print('vWxH text: '+str(vWxH)+', lenght: '+str(len(vWxH))+', vWxH[0]: '+str(vWxH[0]))
    print('vHmin: '+str(vHmin)+', vHmax: '+str(vHmax))
  if (len(vWxH)==1):
    FileName += ' '+vWxH[0]
  elif (len(vWxH)>1):
    if (int(vHmax)/int(vHmin)>vDimLimit):
      if (len(vHFull)==2):
        FileName += ' '+str(vHmin)+jGen+str(vHmax)+'p'
      elif (len(vHFull)>2):
        FileName += ' '+str(vHmin)+jRange+str(vHmax)+'p'
    else:
      FileName += ' ~'+str(vHavg)+'p'
  if debug>2: print('Debug getNFOname, FileName+vWxH: ' + str(FileName))

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
  if debug>2:
    print("vDict['vBR']→unique values→integers")
    print('\tvBR:'+str(vDict['vBR']) +'\t→ '+str(unique(vDict['vBR']))+'\t→ '+str(vBR))
    print('Debug getNFOname, FileName+BitRate: ' + str(FileName))

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
  if debug>2:
    print('Uniqe, sorted & -joined:')
    print('...vBD     \t: ' + vBD)
    print('...vrcType \t: ' + vrcType)
    print('...vrcValue\t: ' + vrcValue)

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
  if debug>2: print('Debug getNFOname: Unique aF\t: ' + str(aF))
  FileName = FileName + ', '+str(aF)
  if debug>2: print('Debug getNFOname +aF: ' + str(FileName))

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
  if debug>2:
    print("vDict['aBR']→unique values→integers")
    print('\taBR:'+str(vDict['aBR']) +'\t→ '+str(unique(vDict['aBR']))+'\t→ '+str(aBR))
    print('Debug getNFOname, FileName+BitRate: ' + str(FileName))

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
  aF1	= jGen.join(map(str,(unique(aF1))))
  if debug>2: print('Debug getNFOname: Unique aF1\t: ' + str(aF1))
  FileName = FileName + ', +c'+aComCountI+' '+str(aF1)
  if debug>2: print('Debug getNFOname +aF1: ' + str(FileName))

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
  if debug>2: print('Debug getNFOname +aCh1: ' + str(FileName))

  aBR1     	= list(map(int,(unique(aBR1)))) #unique bitrate#, converted to int for sorting
  aBR1List 	= list(map(int,aBR1)) #non-unique bitrate#, converted to int for averaging
  # aBR1avg	= int(sum(aBR1)/float(len(aBR1)))
  aBR1avg  	= int(sum(aBR1List)/float(len(aBR1List))) 	#average based on full list
  aBR1avg  	= '{:.0fhcss^1}'.format(FileSize(aBR1avg))	#123456 → 123k
  aBR1len  	= len(aBR1)
  if (aBR1len==1):
    FileName += ' '+aBR1avg
  elif (aBR1len>1):
    FileName += ' ~'+aBR1avg
  FileName += NFOSrc
  if debug>2:
    print("vDict['aBR1']→unique values→integers")
    print('\taBR1:'+str(vDict['aBR1']) +'\t→ '+str(unique(vDict['aBR1']))+'\t→ '+str(aBR1))
    print('Debug getNFOname, FileName+BitRate: ' + str(FileName))
  if debug>1: print('Debug getNFOname with Audio2: ' + str(FileName))

  return FileName

def getMediaInfo(mediafile): #pymediainfo import MediaInfo as wrapMI
  MIJSON = wrapMI.parse(mediafile, text=True, mediainfo_options={"Inform": "JSON"})
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
  if debug>4: print(at)
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
  # if debug>1: print('aBitrate \t= {' + aBR +'}')
  aStart,aEnd,aLangI = ('','','')
  if i>0  : aStart = ', +' + aT[:aTMax].lower()+' '	# Limit Title length→lower case
  if i==0 : aEnd = tSub                            	# mark 1st aud stream as having a subtitle
  if aLang!='en': aLangI = ' ' +aLang              	# add language indicator unless 'en'

  data = aStart+aF+' '+aCh+'ch'+' '+str(aBR)+aLangI+aEnd
  # if debug>1: print('data \t= {' + data +'}')
  return data #[, +Title] Codec Channels BitRate +Subtiles (e.g. 'AAC 6ch 192k +sub' or ', +comment AAC 2ch 60k'

def storeFileInfo(vFolder,file,level,fi): #Store info for a video file in a global dictionary
  # Initialize
  global vfDict
  vStreams,aStreams,tStreams = ([],[],[])
  vFile = vFolder + file
  fvbase = os.path.basename(vFile)
  fvname = os.path.splitext(fvbase)[0]
  if debug>3: print ('=Debug: storeFileInfo(' + vFolder +', ' + ', ' + file + ')')
  levelIndent = ' '*2*level
  if not args.silent: print(levelIndent+' '+vFile) # list

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

  if debug>4: print('vStreams∑=' + str(len(vStreams)) + ':' + str(vStreams) + '\n')
  if debug>4: print('aStreams∑=' + str(len(aStreams)) + ':' + str(aStreams) + '\n')
  if debug>4: print('tStreams∑=' + str(len(tStreams)) + ':' + str(tStreams) + '\n')

def setPadValues(filesNo): #set padding values to match the max value in range
  global vFpad,vWpad,vHpad,vBDpad,vBRpad,aFpad,aBRpad,vfDict
  vStreams,aStreams,aBR=([],[],'')
  for fi in range(filesNo): #get aud/video stream data for each file
    vStreams = vfDict[fi]['vStreams']
    aStreams = vfDict[fi]['aStreams']
    for j in range(len(vStreams)): # for each stream, get max length of var to pad to
      if debug>4: print('fvname,fi,j'+"|"+vfDict[fi]['fvname']+"|"+str(fi)+"|"+str(j))
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
  if debug>2: print('vFpad(3)='+str(vFpad) + '|vWpad(3)='+str(vWpad) + '|vHpad(3)='+str(vHpad) + '|vBDpad(1)='+str(vBDpad) + '|vBRpad(3)='+str(vBRpad) + '|aFpad(3)='+str(aFpad) + '|aBRpad(3)='+str(aBRpad))

def LoopFiles(vFolder='.',level=1,each=False): # call FileInfo for videos and self on subfolders
  global writeBuffer,NFOname0
  level += 1
  spacer = indentlevel*level
  if debug>0: print(spacer + '[' + vFolder)

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
        if debug>0: print (spacer + '×' + vFolder + file)

    if filesNo==0:
      if debug>0: print('No video files in this folder: ' + vFolder)
    else:
      Header = H1+'\t'+H2+'\t'+H3+'\n'
      writeBuffer.append(fPrefix + vFolder + '\n' + Header) #Folder header info
      setPadValues(filesNo)
      for i in range(filesNo): writeFileInfo(i)
      NFOname = getNFOname(vFolder)
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
  if debug>0:
    fOut = open(target,'r')
    print(fOut.read())
    fOut.close

  writeBuffer=[]

# Main
parser = argparse.ArgumentParser(description="Create a list of video files with key Vid/Aud info formatted like this\n(tab-separted columns, space-padded values for vertical alignment):\n"+"  "+H1+"\t"+H2+"                       \t"+H3+"""
  N1\t AVC 1920×1080 0.8m  8b      \tEAC3 6ch 640k de
  N2\tHEVC  704× 468 0.6m 10b crf24\t AAC 2ch  66k +sub, +comment AAC 2ch 66k

where
  Vid\tFormat Width×Height Bitrate Bitdepth RateControl Type/Quality
  Aud\t[Track#1] Format #ofChannels Bitrate Language≠en +Subtitle, [Track#2+] +Title ...

...and a summary NFO file name with the list/count/average/range of values:\n  """+NFOPre+"AVC-HEVC 468-1080p 0.6-0.8m 8-10b crf24, AAC-EAC3 2-6ch 66-640k +s, +c AAC 2ch 66k"+NFOSrc+NFOSuf, formatter_class=RawDHF)
group = parser.add_mutually_exclusive_group()
parser.add_argument("input"        	, metavar="InputPath", help="Add /Path/To/Input/Video (or '.' for current folder)")
group.add_argument("-e","--each"   	, action="store_true", help="create one NFO file for each (sub)folder instead of one for all (sub)folders")
parser.add_argument("-s","--silent"	, action="store_true", help="hide list of processed files")
group.add_argument("out"           	, nargs='?',default="/", metavar="OutputName", help='Output file name [default="/": generate from files in the current folder]')
groupI = parser.add_argument_group('optional info arguments')
groupI.add_argument('-v','--version'	, action='version', version='%(prog)s 1.0@20-3')
args = parser.parse_args()
# group.add_argument("-o","--out"	, nargs='?',const="×Output", metavar="Name", help='Output file name [default: "×Output"; no flag: generated from files in the current folder]')
if debug>3: print(args) #print command line ArgumentParser

vSource = os.path.normpath(args.input)
if vSource[-1] != '/': vSource += '/'
if debug>1: print ('==>vSource : ', vSource)

#Create a global dictionary with all a/v info for all a/v files recursively
LoopFiles(vSource,level,args.each) # if -e also writes to file in each folder

if args.out!='/': # use OutputName when it's given ('/' is the value when empty)
  target = os.path.normpath(vSource+args.out) # (Win) converts / to \
  targetInfo = ' (user input)'
else: # Default to auto-generated NFO file name based on the initial folder (unless -e)
  target = os.path.normpath(vSource+NFOPre + NFOname0 + NFOSuf)
  targetInfo = ' (auto-generated)'

if debug>0: print('\n"ListMediaInfo.py ' + vSource + ' ' + target+'"'+targetInfo)

if not args.each: writeBufferToFile(target) # if not -e write to one file for all folders

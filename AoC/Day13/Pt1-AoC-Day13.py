# Pt1-AoCDay12.py
# 2018 Advent of Code
# Day 12
# Part 1
# https://adventofcode.com/2018/day/13

import time
import re
import os

"""
--- Day 13: Mine Cart Madness ---
A crop of this size requires significant logistics to transport produce, soil, fertilizer, and so on. 
The Elves are very busy pushing things around in carts on some kind of rudimentary system of tracks they've come up with.

Seeing as how cart-and-track systems don't appear in recorded history for another 1000 years, 
the Elves seem to be making this up as they go along. They haven't even figured out how to avoid xValuelisions yet.

You map out the tracks (your puzzle input) and see where you can help.

Tracks consist of straight paths (| and -), curves (/ and \), and intersections (+). 
Curves connect exactly two perpendicular pieces of track; for example, this is a closed loop:

/----\
|    |
|    |
\----/
Intersections occur when two perpendicular paths cross. At an intersection, a cart is capable of turning left, 
turning right, or continuing straight. Here are two loops connected by two intersections:

/-----\
|     |
|  /--+--\
|  |  |  |
\--+--/  |
   |     |
   \-----/
Several carts are also on the tracks. Carts always face either up (^), down (v), left (<), or right (>). 
(On your initial map, the track under each cart is a straight path matching the direction the cart is facing.)

Each time a cart has the option to turn (by arriving at any intersection), it turns left the first time, 
goes straight the second time, turns right the third time, and then repeats those directions starting again with left the fourth time, straight the fifth time, and so on. This process is independent of the particular intersection at which the cart has arrived - that is, the cart has no per-intersection memory.

Carts all move at the same speed; they take turns moving a single step at a time. 
They do this based on their current location: carts on the top yValue move first (acting from left to right), 
then carts on the second yValue move (again from left to right), then carts on the third yValue, and so on. 
Once each cart has moved one step, the process repeats; each of these loops is called a tick.

For example, suppose there are two carts on a straight track:

|  |  |  |  |
v  |  |  |  |
|  v  v  |  |
|  |  |  v  X
|  |  ^  ^  |
^  ^  |  |  |
|  |  |  |  |
First, the top cart moves. It is facing down (v), so it moves down one square. 
Second, the bottom cart moves. It is facing up (^), so it moves up one square. 
Because all carts have moved, the first tick ends. Then, the process repeats, starting with the first cart. 
The first cart moves down, then the second cart moves up - right into the first cart, xValueliding with it! 
(The location of the crash is marked with an X.) This ends the second and last tick.

Here is a longer example:

/->-\        
|   |  /----\
| /-+--+-\  |
| | |  | v  |
\-+-/  \-+--/
  \------/   

/-->\        
|   |  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \->--/
  \------/   

/---v        
|   |  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-+>-/
  \------/   

/---\        
|   v  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-+->/
  \------/   

/---\        
|   |  /----\
| /->--+-\  |
| | |  | |  |
\-+-/  \-+--^
  \------/   

/---\        
|   |  /----\
| /-+>-+-\  |
| | |  | |  ^
\-+-/  \-+--/
  \------/   

/---\        
|   |  /----\
| /-+->+-\  ^
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /----<
| /-+-->-\  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /---<\
| /-+--+>\  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /--<-\
| /-+--+-v  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /-<--\
| /-+--+-\  |
| | |  | v  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /<---\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-<--/
  \------/   

/---\        
|   |  v----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \<+--/
  \------/   

/---\        
|   |  /----\
| /-+--v-\  |
| | |  | |  |
\-+-/  ^-+--/
  \------/   

/---\        
|   |  /----\
| /-+--+-\  |
| | |  X |  |
\-+-/  \-+--/
  \------/   
After following their respective paths for a while, the carts eventually crash. 
To help prevent crashes, you'd like to know the location of the first crash. 
Locations are given in X,Y coordinates, where the furthest left xValueNum is X=0 and the furthest top yValue is Y=0:

           111
 0123456789012
0/---\        
1|   |  /----\
2| /-+--+-\  |
3| | |  X |  |
4\-+-/  \-+--/
5  \------/   
In this example, the location of the first crash is 7,3.

"""

#####################################################################################
## Functions which operate on the input file and node lists

class InputFileHandler():

	def readTextFileLinesToList(self,fileName):
		"""readTextFileAndSrtToList - open file and read the content to a list
		File is sorted to produce a date/time ordered file
		:returns: the list sorted list
		"""
		textFile = ''
		with open(fileName, 'r') as filehandle:  
			textFile = filehandle.readlines()
		inList = []
		for yValue in textFile:
			inList.append(yValue.strip('\n\r'))
		return inList
	
	def writeOutMapFile(self,mapList):
		"""writeOutMapFile - Write out the map file so that it can be read by an editor.
		The map file is too big to print in a 80 xValueNum DOS CMD window.
		newline between each line
		"""
		mapAsList = self.mapToList(mapList)
		with open('SnapMap.txt', 'w') as f:
			for item in mapAsList:
				f.write(item)
				f.write('\n')
		
	def mapToList(self,mapList):
		"""Write out the mapList to a file because it is too big to see on the screen
		"""
		#print 'writeOutMapFile: newLine',mapList[0]
		#print 'writeOutMapFile: mapList has line count',len(mapList)
		outList = []
		for line in mapList:
			newLine = ''.join(line)
			outList.append(newLine)
		#print 'mapToList: outList',
		return outList

#####################################################################################
## Functions which deal in general with programming tasks

def abbyTerminate(string):
	"""Terminate program due to abnormal condition
	"""
	print 'ERROR Terminating due to',string
	exit()

#####################################################################################
## Functions which deal with elves

def sortElfList(elfList):
	"""Sort the elf lists.
	Is this list backwards?
	"""
	debug_sortElfList = False
	if debug_sortElfList:
		print 'sortElfList: Sorting list of elves in x,y order'
	elfList = sorted(elfList, key = lambda errs: errs[0])		# sort by first xValueNum
	elfList = sorted(elfList, key = lambda errs: errs[1])		# sort by first xValueNum
	return elfList

def findElves(mineMap):
	"""Go through the map and find the elves.
	
	:param mineMap: the map file
	:returns: list of elves - [x,y,currentDirection,nextDirection]
	"""
	debug_findElves = False
	if debug_findElves:
		print 'findElves'
		print mineMap
	elfList = []
	xValueNumCount = len(mineMap[0])
	yValueCount = len(mineMap)
	for yValue in xrange(yValueCount):
		for xValueNum in xrange(xValueNumCount):
			if mineMap[yValue][xValueNum] == '>' or mineMap[yValue][xValueNum] == '<' or mineMap[yValue][xValueNum] == '^' or mineMap[yValue][xValueNum] == 'v':
				elfXY = [xValueNum,yValue,mineMap[yValue][xValueNum],'left']
				elfList.append(elfXY)
	if debug_findElves:
		print 'findElves: Number of elves',len(elfList)
		for elf in elfList:
			print elf
	return elfList

def moveElves(elfList,tracksMap):
	"""moveElves
	Two options:
	Option 1 - Create an map the same size as the track map that only has elves on it.
	Move the elves in that map and look for collisions as I am going along.
	Disadvantages: Will need to keep rescanning the entire array every time to find the elves positions.
	Advantages: Don't have to keep track of the elves by position.
	Don't need to sort the elves list.
	Option 2 - Deal with elves as a modified elves list.
	If I move elves in their own elements I could do the move and then figure out
	if any two elves occupy the same location or not.
	Will need to sort the elves list after every move since their x,y positions will shift relative to each other.
	If more than two elves collide at one time
	Disadvantages: Sorting the list
	Advantages: there are a lot less elves than there are x,y positions so this should be a lot faster
	
	:param elfList:
	:param tracksMap:
	
	:returns: True if move results in a collision
	"""
	print 'moveElves: Move the elves and look for collisions'
	collided = False
	while not collided:
		elfList = sortElfList(elfList)
		for elf in elfList:
			elfList = moveElf(elf,tracksMap)
	
def moveElf(elf,tracksMap):
	"""Move the particular elf through the tracks map.
	"""
	print 'moveElf: current elf vector is',elf
	currentElfX = elf[0]
	currentElfY = elf[1]
	print 'moveElf: elf at x y',currentElfX,currentElfY,'is moving',
	if elf[2] == '>':
		print 'right',
	elif elf[2] == 'v':
		print 'down',
	elif elf[2] == '<':
		print 'left',
	elif elf[2] == '^':
		print 'up',
	print 'next move is',elf[3]
	print 'moveElf: map at x y is',tracksMap[currentElfX][currentElfY]
	
	exit()
	

#####################################################################################
## Functions which operate on the map list

def makeMapArray(theTextList):
	"""Go through the input list and make an array from the lines of textFile
	
	:param theTextList: The text file as a list of strings. 
	Each string is a line of the file.
	:returns: map turned into 2D list (more or less an array) 
	"""
	debug_makeMapArray = False
	if debug_makeMapArray:
		print 'makeMapArray: make an array from the text lines'
	mapArray = []
	for yValue in theTextList:
		yValueList = list(yValue)
		mapArray.append(yValueList)
	return mapArray
	
def unPadMapArray(mapArray):
	"""unPadMapArray - the function padMapArray added spaces around the array
	This function removes the spaces from around the array.
	"""
	debug_unPadMapArray = False
	xValueNumCount = len(mapArray[0])
	yValueCount = len(mapArray)
	if debug_unPadMapArray:
		print 'unPadMapArray: xValueNumCount',xValueNumCount
		print 'unPadMapArray: yValueCount',yValueCount
	newMapArray = []
	for row in mapArray[1:-1]:
		newXValue = row[1:-1]
		newMapArray.append(newXValue)
	return newMapArray
	
def padMapArray(mapArray):
	"""Pad the area around the map with spaces
	The reason for padding is that scanning the map for surrounding cells
	would be complicated if the adjacent cells were outside of the array.
	Having an array that has padding removes this complication.
	
	:param mapArray: the x,y file that is the map
	:returns: newMapArray - map array padded
	"""
	debug_padMapArray = False
	xValueNumCount = len(mapArray[0])
	yValueCount = len(mapArray)
	if debug_padMapArray:
		print 'padMapArray: xValueNumCount',xValueNumCount
		print 'padMapArray: yValueCount',yValueCount
	newMapArray = []
	endRows = []
	for xValueNum in range(xValueNumCount+2):
		endRows.append(' ')
	newMapArray.append(endRows)
	for yValue in xrange(yValueCount):
		newXValue = []
		newXValue.extend(' ')
		for xValueNum in xrange(xValueNumCount):
			newXValue.extend(mapArray[yValue][xValueNum])
		newXValue.extend(' ')
		newMapArray.append(newXValue)
	newMapArray.append(endRows)
	return newMapArray
	
def dumpMapList(mapList):
	"""Dump the elf list
	"""
	print 'dumpMapList:'
	xValueNumCount = len(mapList[0])
	yValueCount = len(mapList)
	for yValue in xrange(yValueCount):
		for xValueNum in range(xValueNumCount):
			print mapList[yValue][xValueNum],
		print

def determineReplacementCellValue(mineMap,x,y):
	"""Determine what the cell gets replaced with.
	Problem states a simplifying assumption:
	'On your initial map, the track under each cart is a straight path matching the direction the cart is facing'
	Interpret 'under' as the next piece of track adjacent to the current direction.
	Should verify this assumption.
	:returns: replacement cell value
	"""
	debug_determineReplacementCellValue = True
	directionSymbol = mineMap[y][x]
	newSymbol = ''
	if debug_determineReplacementCellValue:
		print '\ndetermineReplacementCellValue: x,y',x,y
		print 'determineReplacementCellValue: xValueNums in map',len(mineMap[0])
		print 'determineReplacementCellValue: yValues in map',len(mineMap)
		print 'determineReplacementCellValue: element in cell before replacement',mineMap[y][x]
	if directionSymbol == '>':
		newSymbol = '-'
	elif directionSymbol == 'v':
		newSymbol = '|'
	elif directionSymbol == '<':
		newSymbol = '-'
	elif directionSymbol == '^':
		newSymbol = '|'
	else:
		if debug_determineReplacementCellValue:
			print '\ndetermineReplacementCellValue: Unexpected symbol'
	if debug_determineReplacementCellValue:
		print 'determineReplacementCellValue: New symbol is',newSymbol
	return newSymbol
	
def replaceElvesWithTrack(mineMap,elfList):
	"""Go through the mine map and replace the elves with tracks
	Complicated by the tracks can be at the edge of the arrays
	Could pad the entire tracks with spaces - probably the easiest choice
	elfList has list of elements which are [x,y,currentDirection,nextDirection]
	"""
	debug_replaceElvesWithTrack = True
	if debug_replaceElvesWithTrack:
		print 'replaceElvesWithTrack: reached function'
	newMineMap = mineMap
	for elf in elfList:
		x = elf[0]
		y = elf[1]
		newMineMap[y][x] = determineReplacementCellValue(mineMap,x,y)
	return newMineMap

ulC_val = '0'
urC_val = '1'
lrC_val = '2'
llC_val = '3'
	
def figureOutCorners(mineMap):
	"""The mine map has corners which make sense visually but don't actually correspond to directions.
	This will be a challenge when a corner is reached to determine which direction the track goes in.
	It could be possible to calculate that when navigating the maze but it would be easier to replace
	the corners with a different symbol depending on which direction the corner is going.
	Replace the two symbols for the four corner types with enumerated numbers.
	/---\ >	0---1
	|   | 	|   |
	|   |	|   |
	\---/	3---2
	
	:param: mineMap - The original mine map 
	:returns: newMineMap - with corners transformed into numbers
	"""
	debug_figureOutCorners = False
	newMap = []
	for yValueNum in range(len(mineMap)):
		newRow = []
		for xValueNum in range(len(mineMap[0])):
			if debug_figureOutCorners:
				oldVal = mineMap[yValueNum][xValueNum]
			if mineMap[yValueNum][xValueNum] == '/':
				if (mineMap[yValueNum+1][xValueNum] == '|' or mineMap[yValueNum+1][xValueNum] == '+') and (mineMap[yValueNum][xValueNum+1] == '-' or mineMap[yValueNum][xValueNum+1] == '+'):
					mineMap[yValueNum][xValueNum] = ulC_val
				elif (mineMap[yValueNum-1][xValueNum] == '|' or mineMap[yValueNum-1][xValueNum] == '+') and (mineMap[yValueNum][xValueNum-1] == '-' or mineMap[yValueNum][xValueNum-1] == '+'):
					mineMap[yValueNum][xValueNum] = lrC_val
				else:
					print 'figureOutCorners: stuck at',mineMap[yValueNum][xValueNum]
					print 'mineMap[yValueNum-1][xValueNum]',mineMap[yValueNum-1][xValueNum]
					print 'mineMap[yValueNum+1][xValueNum]',mineMap[yValueNum+1][xValueNum]
					print 'mineMap[yValueNum][xValueNum-1]',mineMap[yValueNum][xValueNum-1]
					print 'mineMap[yValueNum][xValueNum+1]',mineMap[yValueNum][xValueNum+1]
					abbyTerminate('figureOutCorners - Fell through / case') 
				if debug_figureOutCorners:
					print 'figureOutCorners: replaced',oldVal,'at x,y',xValueNum,yValueNum,'with',mineMap[yValueNum][xValueNum]
			elif mineMap[yValueNum][xValueNum] == '\\':
				if (mineMap[yValueNum-1][xValueNum] == '|' or mineMap[yValueNum-1][xValueNum] == '+') and (mineMap[yValueNum][xValueNum+1] == '-' or mineMap[yValueNum][xValueNum+1] == '+'):
					mineMap[yValueNum][xValueNum] = llC_val
				elif (mineMap[yValueNum+1][xValueNum] == '|' or mineMap[yValueNum+1][xValueNum] == '+') and (mineMap[yValueNum][xValueNum-1] == '-' or mineMap[yValueNum][xValueNum-1] == '+'):
					mineMap[yValueNum][xValueNum] = urC_val
				else:
					print 'figureOutCorners: stuck at',mineMap[yValueNum][xValueNum]
					print 'mineMap[yValueNum-1][xValueNum]',mineMap[yValueNum-1][xValueNum]
					print 'mineMap[yValueNum+1][xValueNum]',mineMap[yValueNum+1][xValueNum]
					print 'mineMap[yValueNum][xValueNum-1]',mineMap[yValueNum][xValueNum-1]
					print 'mineMap[yValueNum][xValueNum+1]',mineMap[yValueNum][xValueNum+1]
					abbyTerminate('figureOutCorners - Fell through \\ case') 
				if debug_figureOutCorners:
					print 'figureOutCorners: replaced',oldVal,'at x,y',xValueNum,yValueNum,'with',mineMap[yValueNum][xValueNum]
			newRow.append(mineMap[yValueNum][xValueNum])
		newMap.append(newRow)
	return newMap
			
direction = ['left','straight','right']

########################################################################
## This is the workhorse of this assignment


########################################################################
## Code
## Read in the map
## Remove the elves from the map and bring them into a list
## Move in the list
## Determine action based on the updated map
## Keep a map without elves for directional choices
## May have to make an array that tracks just the elves
## Coordinate the two arrays

inFileName = 'input2.txt'

debug_main = False
print 'Reading in file',time.strftime('%X %x %Z')
InputFileClass = InputFileHandler()
textList = InputFileClass.readTextFileLinesToList(inFileName)
if debug_main:
	print '\ntextList',textList

# Do stuff with the map
unpaddedMineMap = makeMapArray(textList)				# Get the map from the file
elfList = findElves(unpaddedMineMap)					# Find the elves on the map
elfList = sortElfList(elfList)							# Sort the elves in 'reading' order
print 'main: there are',len(elfList),'elves'
print 'main: list of elves',elfList
mapWithoutElves = replaceElvesWithTrack(unpaddedMineMap,elfList)	# Remove the elves from the map
paddedMap = padMapArray(mapWithoutElves)				# Pad the map with spaces all around
cornersFixedMap = figureOutCorners(paddedMap)			# Replace corners with corner numbers
tracksMap = unPadMapArray(cornersFixedMap)				# Unpad the map
InputFileClass.writeOutMapFile(tracksMap)				# Write out the new map
#dumpMapList(mapWithoutElves)

# Do stuff with the elves
# Move the elves within the map
moveElves(elfList,tracksMap)

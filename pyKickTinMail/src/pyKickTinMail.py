"""
TindieMail.py - Automate Kickstarter and Tindie shipping lists.

--------
Features
--------

* Input is the csv file as exported from Kickstarter or Tindie 
* Program provides input field flexibility to allow for some column moving
* There are two possible files output
* Files are only produced for items which have not yet shippped.
* One of the output formts is USPS formated CSV file (used fot foreign shipping)
* The other output format is PauPal formated CSV file for US shipping

-----------------
Tindie Input File
-----------------

How to export the file from Tindie

* Tindie
* Menu
* My Store
* Export CSV

----------------------
Kickstarter Input File
----------------------

How to export the file from Kickstarter

* Kickstarter
* Menu (on)
* Backer Report
* Export
* All Reward Tiers
* Save to ZIP
* Extract/combine into CSV file(s)

----
Code
----

"""

import pygtk
pygtk.require('2.0')

import gtk

# Check for new pygtk: this is new class in PyGtk 2.4
if gtk.pygtk_version < (2,3,90):
	 print "PyGtk 2.3.90 or later required"
	 raise SystemExit

import csv
import string
import os
import sys

sys.path.append('C:\\Users\\doug_000\\Documents\\GitHub\\lb-Python-Code\\dgCommonModules')
sys.path.append('C:\\Users\\DGilliland\\Documents\\GitHub\\lb-Python-Code\\dgCommonModules')

from dgProgDefaults import *
from dgReadCSVtoList import *
from dgWriteListtoCSV import *
defaultPath = '.'

# From Tindie
shippingFirstNameColumn = 99
shippingLastNameColumn = 99
address1Column = 99
cityColumn = 99
stateColumn = 99
countryColumn = 99
zipColumn = 99
emailColumn = 99
rewardsSentColumn = 99

# From Kickstarter
shippingNameColumn = 99
address2Column = 99
shippingAmtColumn = 99
rewardMinimumColumn = 99
pledgeAmountColumn = 99
surveyResponseColumn = 99

def errorDialog(errorString):
	"""Prints an error message as a dialog box.

	:param errorDialog: The error message to print
	
	"""
	message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
	message.set_markup(errorString)
	message.run()		# Display the dialog box and hang around waiting for the "OK" button
	message.destroy()	# Takes down the dialog box

class ControlClass:
	"""Methods to read tindie file and write out USPS and PayPal lists.
	"""
	def theExecutive(self):
		"""The code that calls the other code
		"""
		global defaultPath
		
		defaultParmsClass = HandleDefault()
		defaultParmsClass.initDefaults()
		defaultPath = defaultParmsClass.getKeyVal('DEFAULT_PATH')
		print 'defaultPath',defaultPath
		myCSVFileReadClass = ReadCSVtoList()	# instantiate the class
		myCSVFileReadClass.setVerboseMode(True)	# turn on verbose mode until all is working 

		doneReading = False
		firstLine = []
		accumList = []
		while not doneReading:		# if the list is a Kickstarter list then keep reading until cancel
			theInList = myCSVFileReadClass.findOpenReadCSV(defaultPath,'Select CSV File')	# read in CSV into list
			if theInList == []:
				doneReading = True
				break
			inFileType = self.determineInputFileType(theInList[0])
			if inFileType == 2:			# Tindie list type only goes through once
				doneReading = True
				accumList = theInList
				break
			else:
				firstLine = theInList[0]
				for row in theInList[1:]:
					accumList.append(row)
		endList = firstLine
		endList += accumList
		print 'list is lines', len(endList)
#		print 'endList', endList

		if inFileType == 1:		# Kickstarter
			self.mapKickInList(endList[0])
			self.countKickBoards(endList[1:])
			uspsList = self.createKickUSPSAddrList(endList[1:])
			payPalList = self.createKickPayPalAddrList(endList[1:])
		elif inFileType == 2:	# Tindie
			print 'first row of list is', endList[0]
			print 'second row of list is', endList[1]
			self.mapTindieInList(endList[0])
			uspsList = self.createTindieUSPSAddrList(endList[1:])
			payPalList = self.createTindiePayPayAddrList(endList[1:])
			outMessage = 'TindieMail Statistics\n'
			outMessage += 'Unfiltered list lines : '
			outMessage += str(len(endList))
			outMessage += '\nUSPS list lines : '
			outMessage += str(len(uspsList))
			outMessage += '\nPayPal list lines : '
			outMessage += str(len(payPalList))
			errorDialog(outMessage)
		else:
			errorDialog('Could not determine input file type')
			exit()
		defaultPath = myCSVFileReadClass.getLastPath()
		defaultParmsClass.storeKeyValuePair('DEFAULT_PATH',defaultPath)

		fileToWriteUSPS = defaultPath + "orders_USPS.csv"
		fileToWritePayPal = defaultPath + "orders_PayPal.csv"

		outFileClass = WriteListtoCSV()
		outFileClass.appendOutFileName('.csv')
		if uspsList != []:
			uspsHeader = ['First Name','MI','Last Name','Company','Address 1','Address 2','Address 3','City','State/Province','ZIP/Postal Code','Country','Urbanization','Phone Number','Fax Number','E Mail','Reference Number','Nickname']
			outFileClass.writeOutList(fileToWriteUSPS, uspsHeader, uspsList)
		if payPalList != []:
			payPalHeader = ['First Name','MI','Last Name','Company','Address 1','Address 2','Address 3','City','State/Province','ZIP/Postal Code','Country','Urbanization','Phone Number','Fax Number','E Mail','Reference Number','Nickname']
			outFileClass.writeOutList(fileToWritePayPal, payPalHeader, payPalList)
		
	def mapKickInList(self, header):
		"""Map the column headers to an internal preferred ordering.
		Latest input format -
		
		* Backer Number,
		* Backer UID,
		* Backer Name,
		* Email,
		* Shipping Country,
		* Shipping Amount,
		* Reward Minimum,
		* Pledge Amount,
		* Pledged At,
		* Rewards Sent?,
		* Pledged Status,
		* Notes,
		* Survey Response,
		* Shipping Name,
		* Shipping Address 1,
		* Shipping Address 2,
		* Shipping City,
		* Shipping State,
		* Shipping Postal Code,
		* Shipping Country Name,			
		* Shipping Country Code
		
		:param theInList: The entire input list.
		:return: a mapping file with the columns mapped to a column number.

		"""
		global emailColumn
		global countryColumn
		global shippingAmtColumn
		global rewardMinimumColumn
		global pledgeAmountColumn
		global rewardsSentColumn
		global shippingNameColumn
		global address1Column
		global address2Column
		global cityColumn
		global stateColumn
		global zipColumn
		global countryColumn
		global surveyResponseColumn
		myOutList = []
		itemNum = 0
		for item in header:
			if item == 'Email':
				emailColumn = itemNum
			elif item == 'Shipping Country':
				countryColumn = itemNum
			elif item == 'Shipping Amount':
				shippingAmtColumn = itemNum
			elif item == 'Reward Minimum':
				rewardMinimumColumn = itemNum
			elif item == 'Pledge Amount':
				pledgeAmountColumn = itemNum
			elif item == 'Rewards Sent?':
				rewardsSentColumn = itemNum
			elif item == 'Shipping Name':
				shippingNameColumn = itemNum
			elif item == 'Shipping Address 1':
				address1Column = itemNum
			elif item == 'Shipping Address 2':
				address2Column = itemNum
			elif item == 'Shipping City':
				cityColumn = itemNum
			elif item == 'Shipping State':
				stateColumn = itemNum
			elif item == 'Shipping Postal Code':
				zipColumn = itemNum
			elif item == 'Shipping Country Name':
				countryColumn = itemNum
			elif item == 'Survey Response':
				surveyResponseColumn = itemNum
			itemNum += 1
		# print 'header columns', itemNum
		return

	def countKickBoards(self, theInList):
		"""Count the boards and generate a snapshot of the data.
		
		* 4 - Shipping Amount, $5.00 USD
		* 5 - Reward Minimum,
		* 6 - Pledge Amount,
			
		:param theInList: The entire list
		:return: no value
		"""
		global emailColumn
		global countryColumn
		global shippingAmtColumn
		global rewardMinimumColumn
		global pledgeAmountColumn
		global rewardsSentColumn
		global shippingNameColumn
		global address1Column
		global address2Column
		global cityColumn
		global stateColumn
		global zipColumn
		global countryColumn
		global surveyResponseColumn
		boardsCount = 0.0
		unshippedBoardsCount = 0.0
		shippingTotal = 0.0
		rewardTotal = 0.0
		pledgeTotal = 0.0
		backers = 0
		unshippedBackers = 0
		for row in theInList:
			num = 0.0
			print 'row',row
			shippingString = row[shippingAmtColumn][1:-4]
			rewardString = row[rewardMinimumColumn][1:-4]
			pledgeString = row[pledgeAmountColumn][1:-4]
			shippingNum = float(shippingString)
			shippingTotal += shippingNum
			rewardNum = float(rewardString)
			rewardTotal += rewardNum
			pledgeNum = float(pledgeString)
			pledgeTotal += pledgeNum
			# print 'boards', (pledgeNum - shippingNum) / rewardNum
			boardsCount += (pledgeNum - shippingNum) / rewardNum
			# print shippingString, rewardString, pledgeString, (pledgeNum - shippingNum) / rewardNum
			if row[rewardsSentColumn] != 'Sent':
				unshippedBoardsCount += (pledgeNum - shippingNum) / rewardNum
				unshippedBackers += 1
			backers += 1
		outStr = 'Total Backers = '
		outStr += str(backers)
		outStr += '\nTotal Rewards = '
		#{0:.3f}.'.format(boardsCount)
		outStr += '{0:.2f}'.format(boardsCount)
#		outStr += str(boardsCount)
		outStr += '\n-\nUnshipped Backers = '
		outStr += str(unshippedBackers)
		outStr += '\nUnshipped Boards = '
		outStr += str(unshippedBoardsCount)
		outStr += '\n-\nTotal Shipping = $'
		outStr += '{0:.2f}'.format(shippingTotal)
		outStr += '\nTotal Pledges = $'
		outStr += '{0:.2f}'.format(pledgeTotal)
		outStr += '\nAvg $ per board = $'
		outStr += '{0:.2f}'.format((pledgeTotal-shippingTotal)/boardsCount)
		errorDialog(outStr)
	
	def createKickUSPSAddrList(self, theList):
		"""Write out the USPS Address book values.
		The output file is a CSV that can be read by the USPS Address Book Import.
		
		Output list -
		
		* 0 - First Name,
		* 1 - MI,
		* 2 - Last Name,
		* 3 - Company,
		* 4 - Address 1,
		* 5 - Address 2,
		* 6 - Address 3,
		* 7 - City,
		* 8 - State/Province,
		* 9 - ZIP/Postal Code,
		* 10 - Country,
		* 11 - Urbanization (relates to Puerto Rico)
		* 12 - Phone Number,
		* 13 - Fax Number,
		* 14 - E Mail,
		* 15 - Reference Number,
		* 16 - Nickname,,,
		
		:param outFilePtr: points to the output file
		:return: no return value
		"""
		global emailColumn
		global countryColumn
		global shippingAmtColumn
		global rewardMinimumColumn
		global pledgeAmountColumn
		global rewardsSentColumn
		global shippingNameColumn
		global address1Column
		global address2Column
		global cityColumn
		global stateColumn
		global zipColumn
		global surveyResponseColumn
		outList = []
		for row in theList[1:]:
			if len(row) > 12:
				if (row[rewardsSentColumn] == '') and (row[address1Column] != '') and (row[countryColumn] != 'United States'):
					outLine = []
					firstName = row[shippingNameColumn][0:row[shippingNameColumn].find(' ')]
					lastName = row[shippingNameColumn][row[shippingNameColumn].rfind(' ')+1:]
					if row[shippingNameColumn].find(' ') < row[shippingNameColumn].rfind(' '):
						middleInit = row[shippingNameColumn][row[shippingNameColumn].find(' '):row[shippingNameColumn].find(' ')+2]
					else:
						middleInit = ''
					outLine.append(firstName)
					outLine.append(middleInit)
					outLine.append(lastName)
					outLine.append('')
					outLine.append(row[address1Column])
					outLine.append(row[address2Column])
					outLine.append('')
					outLine.append(row[cityColumn])
					outLine.append(row[stateColumn])
					outLine.append(row[zipColumn])
					if row[countryColumn] == 'United Kingdom':
						outLine.append('GREAT BRITAIN AND NORTHERN IRELAND')
					else:
						outLine.append(row[countryColumn])
					outLine.append('')
					outLine.append('')
					outLine.append('')
					outLine.append(row[emailColumn])
					outList.append(outLine)
		return outLine

	def createKickPayPalAddrList(self, theList):
		"""Write out the USPS Address book values.
		The output file is a CSV that can be read by the USPS Address Book Import.
		
		Output list -
		
		* 0 - First Name,
		* 1 - MI,
		* 2 - Last Name,
		* 3 - Company,
		* 4 - Address 1,
		* 5 - Address 2,
		* 6 - Address 3,
		* 7 - City,
		* 8 - State/Province,
		* 9 - ZIP/Postal Code,
		* 10 - Country,
		* 11 - Urbanization (relates to Puerto Rico)
		* 12 - Phone Number,
		* 13 - Fax Number,
		* 14 - E Mail,
		* 15 - Reference Number,
		* 16 - Nickname,,,
		
		:param outFilePtr: points to the output file
		:return: no return value
		"""
		global emailColumn
		global countryColumn
		global shippingAmtColumn
		global rewardMinimumColumn
		global pledgeAmountColumn
		global rewardsSentColumn
		global shippingNameColumn
		global address1Column
		global address2Column
		global cityColumn
		global stateColumn
		global zipColumn
		global surveyResponseColumn
		outLine = []
		for row in theList[1:]:
			if len(row) > 12:
				# print 'country', row[countryColumn]
				if (row[rewardsSentColumn] == '') and (row[address1Column] != '') and (row[countryColumn] == 'United States'):
					outLine = []
					firstName = row[shippingNameColumn][0:row[shippingNameColumn].find(' ')]
					lastName = row[shippingNameColumn][row[shippingNameColumn].rfind(' ')+1:]
					if row[shippingNameColumn].find(' ') < row[shippingNameColumn].rfind(' '):
						middleInit = row[shippingNameColumn][row[shippingNameColumn].find(' '):row[shippingNameColumn].find(' ')+2]
					else:
						middleInit = ''
					outLine.append(firstName)
					outLine.append(middleInit)
					outLine.append(lastName)
					outLine.append('')
					outLine.append(row[address1Column])
					outLine.append(row[address2Column])
					outLine.append('')
					outLine.append(row[cityColumn])
					outLine.append(row[stateColumn])
					outLine.append(row[zipColumn])
					outLine.append(row[countryColumn])
					outLine.append('')
					outLine.append('')
					outLine.append('')
					outLine.append(row[emailColumn])
					outLine.append(outLine)
					
	def determineInputFileType(self, theInList):
		"""Look at the top row of the file to determine the input file type.
		
		:params theInList: Top row of the file
		"""
		if theInList[0] == 'Backer Id':	# Kickstarter
			return 1
		elif theInList[0] == '\xef\xbb\xbfID' or theInList[0] == 'ID':		# Tindie
			return 2
		else:
			print 'first line', theInList
			errorDialog('determineInputFileType: Unable to detect the input file format\nExiting')
			exit()
	
	def mapTindieInList(self, header):
		"""Map the column headers to an internal preferred ordering.
		Latest input format -
		* ID
		* Date
		* First Name
		* Last Name
		* Street
		* City
		* State / Province
		* Postal/Zip Code
		* Country
		* Additional Instructions
		* Email
		* Phone	
		* Refunded
		* Shipped
		* Pay Out Status
		* Paid Out
		* Shipping
		* Shipping Amount 
		* Tracking Number
		* Tindie Fee
		* Processing Fee
		* Product Name
		* Option Summary
		* Status
		* Quantity
		* Unit Price
		* Total Price
		* Model Number

		:param theInList: The entire input list.
		:return: a mapping file with the columns mapped to a column number.

		"""
		global emailColumn
		global shippingFirstNameColumn
		global shippingLastNameColumn
		global address1Column
		global cityColumn
		global stateColumn
		global zipColumn
		global countryColumn
		global rewardsSentColumn
		#print header
		myOutList = []
		itemNum = 0
		for item in header:
			if item == 'Email':
				emailColumn = itemNum
			elif item == 'First Name':
				shippingFirstNameColumn = itemNum
			elif item == 'Last Name':
				shippingLastNameColumn = itemNum
			elif item == 'Country':
				countryColumn = itemNum
			elif item == 'Shipped':
				rewardsSentColumn = itemNum
			elif item == 'Shipping Name':
				shippingNameColumn = itemNum
			elif item == 'Street':
				address1Column = itemNum
			elif item == 'Shipping Address 2':
				address2Column = itemNum
			elif item == 'City':
				cityColumn = itemNum
			elif item == 'State / Province':
				stateColumn = itemNum
			elif item == 'Postal/Zip Code':
				zipColumn = itemNum
			#else:
				#print 'unknown/unused header',item
			itemNum += 1
		return

	def createTindieUSPSAddrList(self, theList):
		"""Write out the USPS Address book values.
		The output file is a CSV that can be read by the USPS Address Book Import.
		
		Output list -
		
		* 0 - First Name,
		* 1 - MI,
		* 2 - Last Name,
		* 3 - Company,
		* 4 - Address 1,
		* 5 - Address 2,
		* 6 - Address 3,
		* 7 - City,
		* 8 - State/Province,
		* 9 - ZIP/Postal Code,
		* 10 - Country,
		* 11 - Urbanization (relates to Puerto Rico)
		* 12 - Phone Number,
		* 13 - Fax Number,
		* 14 - E Mail,
		* 15 - Reference Number,
		* 16 - Nickname,,,
		
		:param outFilePtr: points to the output file
		:return: no return value
		"""
		global emailColumn
		global shippingFirstNameColumn
		global shippingLastNameColumn
		global address1Column
		global cityColumn
		global stateColumn
		global zipColumn
		global countryColumn
		global rewardsSentColumn
		outList = []
		for entryInRow in theList:
			if entryInRow == []:
				break
			if ((entryInRow[rewardsSentColumn] == 'False') or (entryInRow[rewardsSentColumn] == 'FALSE')) and (entryInRow[countryColumn] != 'United States'):
				outLine = []
				outLine.append(entryInRow[shippingFirstNameColumn])
				outLine.append('')
				outLine.append(entryInRow[shippingLastNameColumn])
				outLine.append('')
				outLine.append(entryInRow[address1Column])
				outLine.append('')
				outLine.append('')
				outLine.append(entryInRow[cityColumn])
				outLine.append(entryInRow[stateColumn])
				outLine.append(entryInRow[zipColumn])
				if entryInRow[countryColumn] == 'United Kingdom':
					outLine.append('GREAT BRITAIN AND NORTHERN IRELAND')
				else:
					outLine.append(entryInRow[countryColumn])
				outLine.append('')
				outLine.append('')
				outLine.append('')
				outLine.append(entryInRow[emailColumn])
				outList.append(outLine)
		return outList

	def createTindiePayPayAddrList(self, theList):
		"""Write out the USPS Address book values.
		The output file is a CSV that can be read by the USPS Address Book Import.
		
		Output list -
		
		* 0 - First Name,
		* 1 - MI,
		* 2 - Last Name,
		* 3 - Company,
		* 4 - Address 1,
		* 5 - Address 2,
		* 6 - Address 3,
		* 7 - City,
		* 8 - State/Province,
		* 9 - ZIP/Postal Code,
		* 10 - Country,
		* 11 - Urbanization (relates to Puerto Rico)
		* 12 - Phone Number,
		* 13 - Fax Number,
		* 14 - E Mail,
		* 15 - Reference Number,
		* 16 - Nickname,,,
		
		:param outFilePtr: points to the output file
		:return: no return value
		"""
		global emailColumn
		global shippingFirstNameColumn
		global shippingLastNameColumn
		global address1Column
		global cityColumn
		global stateColumn
		global zipColumn
		global countryColumn
		global rewardsSentColumn
		outList = []
		for row in theList:
			if ((row[rewardsSentColumn] == 'False') or (row[rewardsSentColumn] == 'FALSE')) and (row[countryColumn] == 'United States'):
			#print 'country', row[countryColumn]
				outLine = []
				outLine.append(row[shippingFirstNameColumn])
				outLine.append('')
				outLine.append(row[shippingLastNameColumn])
				outLine.append('')
				outLine.append(row[address1Column])
				outLine.append('')
				outLine.append('')
				outLine.append(row[cityColumn])
				outLine.append(row[stateColumn])
				outLine.append(row[zipColumn])
				outLine.append(row[countryColumn])
				outLine.append('')
				outLine.append('')
				outLine.append('')
				outLine.append(row[emailColumn])
				outList.append(outLine)
		return outList


class UIManager:
	"""The UI manager
	"""
	interface = """
	<ui>
		<menubar name="MenuBar">
			<menu action="File">
				<menuitem action="Open"/>
				<menuitem action="Quit"/>
			</menu>
			<menu action="Help">
				<menuitem action="About"/>
			</menu>
		</menubar>
	</ui>
	"""

	def __init__(self):
		"""Initialize the class
		"""
		# Create the top level window
		window = gtk.Window()
		window.connect('destroy', lambda w: gtk.main_quit())
		window.set_default_size(200, 200)
		
		vbox = gtk.VBox()
		
		# Create a UIManager instance
		uimanager = gtk.UIManager()

		# Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		window.add_accel_group(accelgroup)
		window.set_title('TindieMail - Kickkstarter rewards processing program')

		# Create an ActionGroup
		actiongroup =	gtk.ActionGroup("TindieMail")
		self.actiongroup = actiongroup

		# Create actions
		self.actiongroup.add_actions([
									("Open", gtk.STOCK_OPEN, "_Open", None, "Open an Existing Document", self.openIF),
									("Quit", gtk.STOCK_QUIT, "_Quit", None, "Quit the Application", self.quit_application),
									("File", None, "_File"),
									("Help", None, "_Help"),
									("About", None, "_About", None, "About TindieMail", self.about_TindieMail),
									])
		uimanager.insert_action_group(self.actiongroup, 0)
		uimanager.add_ui_from_string(self.interface)
		
		menubar = uimanager.get_widget("/MenuBar")
		vbox.pack_start(menubar, False)
		
		window.connect("destroy", lambda w: gtk.main_quit())
		
		window.add(vbox)
		window.show_all()

	def openIF(self, b):
		"""Open the interface by calling the control class
		"""
		myControl = ControlClass()
		myControl.theExecutive()

		message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		message.set_markup("Processing Complete")
		message.run()		# Display the dialog box and hang around waiting for the "OK" button
		message.destroy()	# Takes down the dialog box
		return

	def about_TindieMail(self, b):
		"""The about dialog
		"""
		message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		message.set_markup("About TindieMail\nAuthor: Doug Gilliland\n(c) 2015 - land-boards.com - All rights reserved\nTindieMail - Process Timdie orders.cav.\nCreates USPS and PayPal mail order list.")
		message.run()
		message.destroy()
		return

	def quit_application(self, widget):
		gtk.main_quit()

if __name__ == '__main__':
	ba = UIManager()
	gtk.main()
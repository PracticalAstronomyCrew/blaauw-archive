


SQLite output:

fiel: DB_logrows

Tables:

ObservationDays
In each item:
	- DAY_ID
	- ObsDate

Logsheets
In each item:
	- ROW_ID
	- LogSheetfile
	- ObsDate

ScanRows
In each item:
	- ROW_ID
	- ObsDate
	- LogSheetFile
	- RowNum
	- Interpreter
	- GoogleVision
	- BlopFile
	- CALMatch
	- SIMMatch
	- MPCMatch
	- Flag_Nomatch
	- Flag_Interpreter


The following does not exist yet but will contain the transcripts of the logsheets
Transcripts
In each item: 		Not sure how I am going to do naming convention yet, most liekly by log sheet file name
	- ObsDate		
	- LogSheetFile
	- Completed
	- Day_ID
	transcript 			This will be a sublist containing the transcript, if SQL doesn’t support this I will just add the content below this
		- Observers
		- Supervisor
		- Date
		- Page		Under Page separate sublist (again provided it is an option)
			- Page_number
			- Row1 (sublist again)
				-    Cell1
				- ….
				-    Cell12				Cell nr might have differed based on when the log sheet was made, have to look into it
			- Row2
				-    Cell1
				- ….
				-    Cell12
			- Row3
			- ….

		- Out of bounds text will get an extra section, unless I figure out a way to append it to the correct cell, with reference to which cell it most probably belonged

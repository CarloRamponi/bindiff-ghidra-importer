#Import symbols from bindiff file.
#@author Carlo Ramponi
#@category bindiff scripts
#@menupath 
#@toolbar 

import sys
from ghidra.program.model.symbol.SourceType import *

class Column():
    SIMILARITY = 0
    CONFIDENCE = 1
    PRIMARY_ADDRESS = 2
    PRIMARY_NAME = 3
    PRIMARY_TYPE = 4
    SECONDARY_ADDRESS = 5
    SECONDARY_NAME = 6
    SECONDARY_TYPE = 7

file = askFile("bindiff script", "choose the CSV file")
try:
    print("Trying to open: {}".format(file))
    with open(file.toString(), "r") as file:
        csv = [l.split("\t")[1:9] for l in file.readlines()]
except:
    popup("Unable to open file for reading")
    sys.exit(-1)

while True:
    min_confidece = askDouble("bindiff script", "Minimum confidence")

    if min_confidece > 1.0 or min_confidece < 0.0:
        popup("{} is not in the interval [0, 1]".format(min_confidece))
    else:
        break

while True:
    min_similarity = askDouble("bindiff script", "Minimum similarity")
    if min_similarity > 1.0 or min_similarity < 0.0:
        popup("{} is not in the interval [0, 1]".format(min_similarity))
    else:
        break

total_functions = len(csv)
# Filter out the results

def filterFn(line):
    # confidence:
    if float(line[Column.CONFIDENCE]) < min_confidece:
        return False
    
    # similarity
    if float(line[Column.SIMILARITY]) < min_similarity:
        return False

    # unrecognized functions
    name = line[Column.SECONDARY_NAME]
    if name.startswith("thunk_") or name.startswith("sub_"):
        return False

    return True

csv = filter(filterFn, csv)

proceed = askYesNo("bindiff script", "Total matches: {}\nFiltered matched: {}\nProceed?".format(total_functions, len(csv)))

if not proceed:
    sys.exit(0)

for line in csv:
    print("Renaming function at {} ({}) to {}".format(hex(int(line[Column.PRIMARY_ADDRESS], 16)), line[Column.PRIMARY_NAME], line[Column.SECONDARY_NAME]))
    address = currentProgram.getAddressFactory().getAddress(line[Column.PRIMARY_ADDRESS])
    func = getFunctionAt(address)
    if func is not None:
        func.setName(line[Column.SECONDARY_NAME], USER_DEFINED)
        print("Function %s renamed as %s" % (line[Column.PRIMARY_NAME], line[Column.SECONDARY_NAME]))
    else:
        func = createFunction(address, line[Column.SECONDARY_NAME])
        print("New function created: %s" % line[Column.SECONDARY_NAME])

# Output to a popup window
# popup(val)

# # Add a comment to the current program
# minAddress = currentProgram.getMinAddress()
# listing = currentProgram.getListing()
# codeUnit = listing.getCodeUnitAt(minAddress)
# codeUnit.setComment(codeUnit.PLATE_COMMENT, "This is an added comment!")

# # Get a data type from the user
# from ghidra.app.util.datatype import DataTypeSelectionDialog
# from ghidra.util.data.DataTypeParser import AllowedDataTypes
# tool = state.getTool()
# dtm = currentProgram.getDataTypeManager()
# selectionDialog = DataTypeSelectionDialog(tool, dtm, -1, AllowedDataTypes.FIXED_LENGTH)
# tool.showDialog(selectionDialog)
# dataType = selectionDialog.getUserChosenDataType()
# if dataType != None: print "Chosen data type: " + str(dataType)

# # Report progress to the GUI.  Do this in all script loops!
# import time
# monitor.initialize(10)
# for i in range(10):
#     monitor.checkCanceled() # check to see if the user clicked cancel
#     time.sleep(1) # pause a bit so we can see progress
#     monitor.incrementProgress(1) # update the progress
#     monitor.setMessage("Working on " + str(i)) # update the status message

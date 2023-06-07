# Mu2eCaloDMAP

## Original version
Run it using source runall.sh. It creates (besides intermediate steps) a final.dat file

## New version 
Run it just by executing the Python code. It creates a dmap.csv file, containing cryID, rouID(2 x cryID + 0/1), local (1-20) and global (20 x board + local) channel numbers, besides all the info coming from the original Excel file. It is way more compact and editable than the original version but slower, due to Python opening the .xlsx file.

## Requirements
Files needed:
- "Pasciuto"-like .csv file, crystalpos.h for the original version
- "Pasciuto"-like .xlsx file, crystalpos.py for the new version.
In order to re-create crystalpos.py from crystalpos.h, just replace brace with square brackets and delete types and include directives.

The Python code requires pandas and numpy libraries

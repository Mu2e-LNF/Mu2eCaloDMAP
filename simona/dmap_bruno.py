import numpy as np

import pandas as pd
import crystalpos

#-----------------------------------------------------------------------------------
# Crystal cabling numbering:
# - Disk:    0-1
# - Phi:     0-1 (xneg-xpos)
# - Crate:   0-4 (bot-top)
# - Board:   0-3 (bot-top)   [1-4 in Bruno's file]
# - Sensor:  0-1 (xneg-xpos)
# - MBconn:  1-5 
# - ConnIdx: 2-5 channel inside MB connector (according to Bruno's numbering)
#            0-3 Using this range instead of ConnIdx for FEEchan evaluation
#-----------------------------------------------------------------------------------
##
## The excel cabling map is not organized for each single readout channel anymore.
## The two RO channels of crystals are on the same row, because with the current
## scheme they have the same MBconn/ConnIdx.
## We have to move back to the old scheme in the DB map, because if we modify some
## connectors during the running, we have to be flexible to insert different
## MBconn/ConnIdx for the two SiPMs of a crystal.
##
#-----------------------------------------------------------------------------------

# Read cabling info
dftmp = pd.read_excel("cabling_disk1.xlsx")

print( "Length of input data frame: ",dftmp.index.size )
print( list(dftmp.columns.values))

# This command re-arrange data format dftmp according to the given variables
# As a result, two rows with different SiPM IDs are created for each dftmp row 
df = dftmp.melt(id_vars=["x", "y","crate","board","BoardChan","MBconn","ConnIdx","phi"])
print( "Length of output data frame: ",len(df) )
print( list(df.columns.values))

#-----------------------------------------------------------------------------------
# Check consistency between MBconn+ConnIdx and BoardChan
#-----------------------------------------------------------------------------------

df["Test1"] = df.ConnIdx-2 + 4*(df.MBconn-1)
df["Test2"] = df.BoardChan-1

if (df["Test1"].equals(df["Test2"]))==False:
    print()
    print("ERROR: MBconn+ConnIdx do not match BoardChan! Aborting...")
    print()
    quit()

#-----------------------------------------------------------------------------------
# Add missing fields:
# - disk (the cabling map does not have the disk field)
# - shift board number from 1-4 to 0-3
# - create sensor column starting from the new column created by .melt command
#-----------------------------------------------------------------------------------

df["disk"] = 1

# *** TEMPORARY *** for BoardIdx testing
#df["disk"] = 0

df["board"] = df["board"].subtract(1)
df["sensor"] = df.value

#-----------------------------------------------------------------------------------
# Global Board index
# This can be done in two different ways:
# - (a) continuous index number, as in Mu2e-doc-37247
# - (b) index with holes, corresponding to not inserted boards in crates (current)
#-----------------------------------------------------------------------------------

df = df.assign(BoardIdx=None)

# Get DIRAC index map considering position in the crate, as in (b)

df["BoardIdx"] = df.sensor + 2*df.board + 2*4*df.crate + 2*4*5*df.phi + 2*4*5*2*df.disk


'''
# Get DIRAC index map according to Mu2e-doc-37247

df_dirac = pd.read_csv("BoardIdx.dat",sep=" ")
print( "Length of output data frame: ",len(df_dirac) )
print( list(df_dirac.columns.values))

for feeIdx in range(0,len(df)):
    for daqIdx in range(0,len(df_dirac)):
        if df_dirac["Disk"].iloc[daqIdx]==df["disk"].iloc[feeIdx] and df_dirac["Phi"].iloc[daqIdx]==df["phi"].iloc[feeIdx]:
            if df_dirac["Crate"].iloc[daqIdx]==df["crate"].iloc[feeIdx] and df_dirac["Board"].iloc[daqIdx]==df["board"].iloc[feeIdx]:
                if df_dirac["Sensor"].iloc[daqIdx]==df["sensor"].iloc[feeIdx]:
                    df["BoardIdx"].at[feeIdx] = df_dirac["BoardIdx"].iloc[daqIdx]
                    #print(df["disk"].iloc[feeIdx],df["phi"].iloc[feeIdx],df["crate"].iloc[feeIdx],df["board"].iloc[feeIdx],df["sensor"].iloc[feeIdx],df["BoardIdx"].at[feeIdx])

# Dump of BoardIdx map
print("Disk Phi Crate Board Sensor BoardIdx")
idxVal = 0
for DiskIdx in range(0,2):
    for Phi_Idx in range(0,2):
        for CratIdx in range(0,5):
            if CratIdx<2:
                nBoards = 4
            else:
                nBoards = 3
            for BoarIdx in range(0,nBoards):
                for SiPMIdx in range(0,2):
                    val = SiPMIdx + 2*BoarIdx + 2*nBoards*CratIdx + 2*nBoards*5*Phi_Idx + 2*nBoards*5*2*DiskIdx
                    print(DiskIdx,Phi_Idx,CratIdx,BoarIdx,SiPMIdx,idxVal)
                    idxVal = idxVal + 1
quit()
'''

#-----------------------------------------------------------------------------------
# Global FEE channel index
# - The index is built assuming all crates with 4 boards
# - The resulting index span 0-3199, and it is not continuous
# - Index holes corresponds to not inserted boards in crates
#-----------------------------------------------------------------------------------

df["FEEchan"] = df.ConnIdx-2 + 4*(df.MBconn-1) + 4*5*df.sensor + 4*5*2*df.board + 4*5*2*4*df.crate + 4*5*2*4*5*df.phi + 4*5*2*4*5*2*df.disk

'''
# Test FEEchan variable
print("FEE index")
for DiskIdx in range(0,2):
    for Phi_Idx in range(0,2):
        for CratIdx in range(0,5):
            for BoarIdx in range(0,4):
                for SiPMIdx in range(0,2):
                    for MBchIdx in range(1,6):
                        for ConnIdx in range(2,6):
                            val = (ConnIdx-2) + 4*(MBchIdx-1) + 4*5*SiPMIdx + 4*5*2*BoarIdx + 4*5*2*4*CratIdx + 4*5*2*4*5*Phi_Idx + 4*5*2*4*5*2*DiskIdx
                            print(ConnIdx,MBchIdx,SiPMIdx,BoarIdx,CratIdx,Phi_Idx,DiskIdx)
#                            print(val)
'''

'''
# Misc's recipe: 0-2695 - Crates 0-1 with 4 boards, crates 2-4 with 3 boards. Compact index.
# This method does not work, since the offset when nBoards=3 does not take into account the
# larger number of indexes filled when nBoards=4

df = df.assign(FEEchan=None)

for feeIdx in range(0,len(df)):
    if df["crate"].at[feeIdx]<2:
        nBoards = 4
    else:
        nBoards = 3
       
    df["FEEchan"].at[feeIdx] = df["ConnIdx"].at[feeIdx]-2 + 4*(df["MBconn"].at[feeIdx]-1) + 4*5*df["sensor"].at[feeIdx] + 4*5*2*df["board"].at[feeIdx] + 4*5*2*nBoards*df["crate"].at[feeIdx] + 4*5*2*nBoards*5*df["phi"].at[feeIdx] + 4*5*2*nBoards*5*2*df["disk"].at[feeIdx]
    #print(df["FEEchan"].at[feeIdx])
'''

'''
# Test of Misc's FEEchan variable
print("FEE index")
for DiskIdx in range(0,2):
    for Phi_Idx in range(0,2):
        for CratIdx in range(0,5):
            if CratIdx<2:
                nBoards = 4
            else:
                nBoards = 3
            for BoarIdx in range(0,nBoards):
                for SiPMIdx in range(0,2):
                    for MBchIdx in range(1,6):
                        for ConnIdx in range(2,6):
                            val = (ConnIdx-2) + 4*(MBchIdx-1) + 4*5*SiPMIdx + 4*5*2*BoarIdx + 4*5*2*4*CratIdx + 4*5*2*4*5*Phi_Idx + 4*5*2*4*5*2*DiskIdx
                            #print(ConnIdx,MBchIdx,SiPMIdx,BoarIdx,CratIdx,Phi_Idx,DiskIdx)
#                            print(val)
'''

#-----------------------------------------------------------------------------------
# Find Offline indexes
#-----------------------------------------------------------------------------------

# Get FEE-Offline index map
df_offl = pd.read_csv("calo_idx.csv",sep=';',header=0)

df = df.assign(xcry=None)
df = df.assign(ycry=None)
df = df.assign(cryID=None)
df = df.assign(rouID=None)
df = df.assign(Type="CAL")

for feeIdx in range(0,len(df)):
    for offIdx in range(0,len(df_offl)):
        if df_offl["idlay"].iloc[offIdx]==df["y"].iloc[feeIdx] and df_offl["idcol"].iloc[offIdx]==df["x"].iloc[feeIdx]:
            df["xcry"].at[feeIdx] = df_offl["xpos"].iloc[offIdx]
            df["ycry"].at[feeIdx] = df_offl["ypos"].iloc[offIdx]
            df["cryID"].at[feeIdx] = df_offl["cryid"].iloc[offIdx]

    # Put CAPHRI flag for the 4 LYSO crystals: Layers 4 and 32, Columns 0 and 24
    if ( df["y"].iloc[feeIdx]==4 or df["y"].iloc[feeIdx]==32 ) and ( df["x"].iloc[feeIdx]==0 or df["x"].iloc[feeIdx]==24 ):
        df["Type"].at[feeIdx] = "CAPHRI"
    # Flag pin-diodes
    if ( pd.isnull(df.loc[feeIdx,"y"]) ):
        df["Type"].at[feeIdx] = "PIN-DIODE"

# This means 0/1 = L/R
df["rouID"] = df.value

#-----------------------------------------------------------------------------------
# Drop unuseful columns, reorder and save
#-----------------------------------------------------------------------------------

df = df.drop("variable", axis=1 )
df = df.drop("value", axis=1 )

df = df[['y','x','disk','phi','crate','board','sensor','BoardIdx','MBconn','ConnIdx','BoardChan','FEEchan','xcry','ycry','cryID','rouID','Type']]
#df = df[['y','x','disk','phi','crate','board','sensor','MBconn','ConnIdx','BoardChan','FEEchan','xcry','ycry','cryID','rouID','Type']]
df.to_excel("dmap_bruno.xlsx")
df.to_csv("dmap_bruno.csv", index=None)

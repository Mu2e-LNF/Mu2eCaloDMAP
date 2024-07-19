from DataLoader_p3 import DataLoader, DataQuery
import csv
#import numpy as np
import pandas as pd

forceError = False  # Set to True to force an error in the data

###################################################################
# DB setup: Mu2e HW DB >>> PRODUCTION <<<
###################################################################

queryUrl = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query"
dataQuery = DataQuery(queryUrl)

#group = "EMC Readout Tables"
table1 = "holder_calibrations"

###################################################################
# Read DMAP *** This is temporary! It must be taken from online DB
###################################################################

#------------------------------------------------------------------
# Crystal cabling numbering:
# - Disk:    0-1
# - Phi:     0-1 (xneg-xpos)
# - Crate:   0-4 (bot-top)
# - Board:   0-3 (bot-top)
# - Sensor:  0-1 (xneg-xpos)
#------------------------------------------------------------------

df_dmap = pd.read_excel("dmap_bruno.xlsx")
df_dmap['BoardChan'] = df_dmap.BoardChan-1

###################################################################
# Order DMAP values by BoardIdx/BoardChan, add Vop
###################################################################

df_dmap = df_dmap.sort_values(['BoardIdx','BoardChan'],ascending=[True,True])

df_dmap['Vop'] = df_dmap['disk']*0.

#df_dmap.to_excel("test.xlsx")
#quit()

###################################################################
# Get Vop: from HWDB for 'CAL'/'CAPHRI' types, fixed for PIN-DIODE
###################################################################

for dmapIdx in range(0,len(df_dmap)):

    iDisk    = int(df_dmap["disk"     ].iat[dmapIdx])
    iPhi     = int(df_dmap["phi"      ].iat[dmapIdx])
    iCrate   = int(df_dmap["crate"    ].iat[dmapIdx])
    iBoard   = int(df_dmap["board"    ].iat[dmapIdx])
    iSiPM    = int(df_dmap["sensor"   ].iat[dmapIdx])
    chType   =     df_dmap["Type"     ].iat[dmapIdx]
    idxDIRAC = int(df_dmap["BoardIdx" ].iat[dmapIdx])
    idxChann = int(df_dmap["BoardChan"].iat[dmapIdx])

    if( df_dmap["Type"].iat[dmapIdx]=='CAL' or df_dmap["Type"].iat[dmapIdx]=='CAPHRI'):
        layer    = int(df_dmap["y"].iat[dmapIdx])
        column   = int(df_dmap["x"].iat[dmapIdx])
        print('DIRAC/Chann/Disk/Phi/Crate/Board/SiPM/Type/layer/column:',idxDIRAC,idxChann,iDisk,iPhi,iCrate,iBoard,iSiPM,chType,layer,column)
        search = 'disk_crymap:eq:' + str(iDisk) + '&layer_crymap:eq:' + str(layer) + '&column_crymap:eq:' + str(column)
        #print(search)
        dbrow = dataQuery.query('mu2e_hardware_prd','calorimeter_maps','holder_id',search,
                            '-create_time',1) # most recent entry
        if dbrow[0][0]!='H':
            print('ERROR: Holder not found for Disk/Phi/Crate/Board/SiPM/layer/column',iDisk,iPhi,iCrate,iBoard,iSiPM,layer,column)
            quit()

        holderId = dbrow[0]

        if iSiPM==0:
            dbrow = dataQuery.query('mu2e_hardware_prd','holder_calibrations','holder_id,vop_0',
                                    'holder_id:eq:%s' % holderId, '-create_time',1)
        elif iSiPM==1:
            dbrow = dataQuery.query('mu2e_hardware_prd','holder_calibrations','holder_id,vop_1',
                                    'holder_id:eq:%s' % holderId, '-create_time',1)
        else:
            print('ERROR: Unknown iSiPM for Disk/Phi/Crate/Board/SiPM:',iDisk,iPhi,iCrate,iBoard,iSiPM)
            quit()
            
        if dbrow[0][0]!='H':
            print('ERROR: Vop not found for holder:',holderId)
            quit()

        print(dbrow[0])
        VopTmp = dbrow[0].split(",")[1]
    elif( df_dmap["Type"].iat[dmapIdx]=='PIN-DIODE' ):
        print('DIRAC/Chann/Disk/Phi/Crate/Board/SiPM/Type:',idxDIRAC,idxChann,iDisk,iPhi,iCrate,iBoard,iSiPM,chType)
        VopTmp = 165.0
    else:
        print('ERROR: Unknown CalType',df_dmap["Type"].iat[dmapIdx],'for Disk/Phi/Crate/Board/SiPM:',iDisk,iPhi,iCrate,iBoard,iSiPM)
        quit()
    
    df_dmap["Vop"].iat[dmapIdx] = VopTmp

###################################################################
# Prepare board configuration files
###################################################################

for iBoard in range(0,160):

    # Check if iBoard exists in DMAP
    if iBoard in df_dmap['BoardIdx'].values:
    
        fileName = 'board' + format(iBoard,'03d') + '.config'
        print(fileName)
        fileOut = open( fileName, 'w' )

        for dmapIdx in range(0,len(df_dmap)):

            if( df_dmap["BoardIdx"].iat[dmapIdx]==iBoard ):

                data = ( format(df_dmap['BoardChan'].iat[dmapIdx],'2d') +
                         '%10.3f' % float(df_dmap['Vop'].iat[dmapIdx])  +
                         '   ' + df_dmap['Type'].iat[dmapIdx] + '\n'    )
                #print ( data )
                
                fileOut.write( data )
                
        fileOut.close()


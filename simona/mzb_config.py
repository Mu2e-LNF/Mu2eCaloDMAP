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

df_dmap['Cal1'] = df_dmap['disk']*20.273
df_dmap['Cal2'] = df_dmap['disk']*-15.862
df_dmap['Cal3'] = df_dmap['disk']*0.0493681
df_dmap['Cal4'] = df_dmap['disk']*0.617098
df_dmap['Cal5'] = df_dmap['disk']*0.6276
df_dmap['Cal6'] = df_dmap['disk']*2.09773
df_dmap['Cal7'] = df_dmap['disk']*-0.06098
df_dmap['Cal8'] = df_dmap['disk']*94.6

#df_dmap.to_excel("test.xlsx")
#quit()

###################################################################
# Get FEE calib: from HWDB for 'CAL'/'CAPHRI' types, ??? for PIN-DIODE
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

    # Get FEE board calibration for calo channels only
    if( df_dmap["Type"].iat[dmapIdx]=='CAL' or df_dmap["Type"].iat[dmapIdx]=='CAPHRI'):
        layer    = int(df_dmap["y"].iat[dmapIdx])
        column   = int(df_dmap["x"].iat[dmapIdx])
        print('DIRAC/Chann/Disk/Phi/Crate/Board/SiPM/Type/layer/column:',idxDIRAC,idxChann,iDisk,iPhi,iCrate,iBoard,iSiPM,chType,layer,column)

        # Inquire calo map table to extract HolderId
        search = 'disk_crymap:eq:' + str(iDisk) + '&layer_crymap:eq:' + str(layer) + '&column_crymap:eq:' + str(column)
        #print(search)
        dbrow = dataQuery.query('mu2e_hardware_prd','calorimeter_maps','holder_id',search,
                                '-create_time',1) # most recent entry
        if dbrow[0][0]!='H':
            print('ERROR: Holder not found for Disk/Phi/Crate/Board/SiPM/layer/column',iDisk,iPhi,iCrate,iBoard,iSiPM,layer,column)
            quit()

        holderId = dbrow[0]

        # Inquire ROU assembly tables to extract FEE board ID
        if iSiPM==0:
            dbrow = dataQuery.query('mu2e_hardware_prd','holder_assemblies','holder_id,production_id_0,fee_board_0',
                                    'holder_id:eq:%s' % holderId, '-create_time',1)
        elif iSiPM==1:
            dbrow = dataQuery.query('mu2e_hardware_prd','holder_assemblies','holder_id,production_id_1,fee_board_1',
                                    'holder_id:eq:%s' % holderId, '-create_time',1)
        else:
            print('ERROR: Unknown iSiPM for Disk/Phi/Crate/Board/SiPM:',iDisk,iPhi,iCrate,iBoard,iSiPM)
            quit()
            
        if dbrow[0][0]!='H':
            print('ERROR: Vop not found for holder:',holderId)
            quit()

        print(dbrow[0])
        Parcel = dbrow[0].split(",")[1]
        FEEIdx = dbrow[0].split(",")[2]

        # Get FEE calib values
        calibString = 'institution,hv_dac_slope,hv_dac_offset,hv_adc_slope,hv_adc_offset,current_adc_slope,current_adc_offset,temperature_adc_slope,temperature_adc_offset'
        search = 'production_id:eq:' + Parcel + '&fee_id:eq:' + FEEIdx
        dbrow = dataQuery.query('mu2e_hardware_prd','fee_calibrations',calibString,search, '-create_time',1)

        if dbrow[0][0]!='L':
            print('ERROR: Calibration not found for FEE board:',Parcel,FEEIdx)
            quit()

        print( dbrow[0] )
        Val1 = float(dbrow[0].split(",")[1])
        Val2 = float(dbrow[0].split(",")[2])
        Val3 = float(dbrow[0].split(",")[3])
        Val4 = float(dbrow[0].split(",")[4])
        Val5 = float(dbrow[0].split(",")[5])
        Val6 = float(dbrow[0].split(",")[6])
        Val7 = float(dbrow[0].split(",")[7])
        Val8 = float(dbrow[0].split(",")[8])
        
    # ???
    elif( df_dmap["Type"].iat[dmapIdx]=='PIN-DIODE' ):
        print('DIRAC/Chann/Disk/Phi/Crate/Board/SiPM/Type:',idxDIRAC,idxChann,iDisk,iPhi,iCrate,iBoard,iSiPM,chType)
    else:
        print('ERROR: Unknown CalType',df_dmap["Type"].iat[dmapIdx],'for Disk/Phi/Crate/Board/SiPM:',iDisk,iPhi,iCrate,iBoard,iSiPM)
        quit()

    df_dmap["Cal1"].iat[dmapIdx] = Val1
    df_dmap["Cal2"].iat[dmapIdx] = Val2
    df_dmap["Cal3"].iat[dmapIdx] = Val3
    df_dmap["Cal4"].iat[dmapIdx] = Val4
    df_dmap["Cal5"].iat[dmapIdx] = Val5
    df_dmap["Cal6"].iat[dmapIdx] = Val6
    df_dmap["Cal7"].iat[dmapIdx] = Val7
    df_dmap["Cal8"].iat[dmapIdx] = Val8
        
###################################################################
# Prepare board configuration files
###################################################################

for iBoard in range(0,160):

    # Check if iBoard exists in DMAP
    if iBoard in df_dmap['BoardIdx'].values:
    
        fileName = 'mzb' + format(iBoard,'03d') + '.config'
        #print(fileName)
        fileOut = open( fileName, 'w' )

        for dmapIdx in range(0,len(df_dmap)):

            if( df_dmap["BoardIdx"].iat[dmapIdx]==iBoard ):

                data = ( format(df_dmap['BoardChan'].iat[dmapIdx],'2d') +
                         '%10.3f' % float(df_dmap['Cal1'].iat[dmapIdx])  +
                         '%10.3f' % float(df_dmap['Cal2'].iat[dmapIdx])  +
                         '%10.7f' % float(df_dmap['Cal3'].iat[dmapIdx])  +
                         '%10.6f' % float(df_dmap['Cal4'].iat[dmapIdx])  +
                         '%10.4f' % float(df_dmap['Cal5'].iat[dmapIdx])  +
                         '%10.5f' % float(df_dmap['Cal6'].iat[dmapIdx])  +
                         '%10.5f' % float(df_dmap['Cal7'].iat[dmapIdx])  +
                         '%10.1f' % float(df_dmap['Cal8'].iat[dmapIdx])  + '\n' )
                print ( data )
                fileOut.write( data )
                
        fileOut.close()


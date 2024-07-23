from DataLoader_p3 import DataLoader, DataQuery
import csv

import pandas as pd

forceError = False  # Set to True to force an error in the data

###################################################################
# DB setup: Mu2e HW DB >>> PRODUCTION <<<
###################################################################

url = "https://dbweb9.fnal.gov:8443/hdb/mu2e/loader"
queryUrl = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query"
dataQuery = DataQuery(queryUrl)

password = "TAbW2xEB"     # Production

group = "EMC Readout Tables"
table1 = "calorimeter_maps"

###################################################################
# Read summary data file
###################################################################

df_dmap = pd.read_excel("cabling_disk1_holders.xlsx")
df_dmap["board"] = df_dmap["board"].subtract(1)

# Get Holder Id for a given x,y pair from csv files dumped from HWDB
#df_hwdb = pd.read_csv("calomap_hwdb.csv",sep=",",header=0)

for dmapIdx in range(0,len(df_dmap)):

    column   = int( df_dmap["x"].iat[dmapIdx] )
    layer    = int( df_dmap["y"].iat[dmapIdx] )
    HolderId = df_dmap["Holder"].iat[dmapIdx]
    iPhi     = int( df_dmap["phy"      ].iat[dmapIdx] )
    iCrate   = int( df_dmap["crate"    ].iat[dmapIdx] )
    iBoard   = int( df_dmap["board"    ].iat[dmapIdx] )

    #print( 'Cell:',column, layer, HolderId )

    # Get Holder Id for a given x,y pair from HWDB calo map.

    dataQuery = DataQuery(queryUrl)
    search = ( 'disk_crymap:eq:1&layer_crymap:eq:' + str(layer) + '&column_crymap:eq:' + str(column) )
    #print( 'search: ',search )
    HolderDB = dataQuery.query('mu2e_hardware_prd','calorimeter_maps','holder_id',search,'-create_time',1)
   
    #pprint('layer/raw/ids:',layer,column,HolderId,HolderDB[0])
    
    if( HolderId!=HolderDB[0] ):
        print('ERROR: Holder number mismatch for layer/raw/phi/crate/board:',layer,column,iPhi,iCrate,iBoard,HolderId,HolderDB )


    


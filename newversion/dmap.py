import numpy as np

import pandas as pd
import crystalpos

df = pd.read_excel("../Crystals naming compact4.xlsx", nrows=10) #1348)

'''
if( Height==0) localch = Row*4+Loc;
if( Height==1) localch = 8+Loc;
if( Height==2) localch = 12+ Row*4+Loc;
'''

df["localch"] = df.height*0

df.localch = df.localch.mask(df.height==0, df.row*4+df.location, axis=0)
df.localch = df.localch.mask(df.height==1, 8+df.location, axis=0)
df.localch = df.localch.mask(df.height==2, 12 + df.row*4+df.location, axis=0)

df["globalch"] = df.localch + 20*df.board

cry_mat = np.asarray([crystalpos.xcry, crystalpos.ycry]).T

df["ycry"] = df.y*34.3 + np.min(cry_mat[:, 1])

df["xcry"] = df.apply(lambda row: np.sort(cry_mat[np.round(cry_mat[:, 1]) == round(row["ycry"])][:, 0])[row.x], axis=1)

df["cryID"] = df.apply(lambda row: np.abs(cry_mat - np.asarray([row.xcry, row.ycry]).T).sum(axis=1).argmin(), axis=1)

df["rouID"] = df.cryID*2 + df.sensor

df.to_csv("dmap.csv", index=None)

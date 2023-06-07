#include <TH2.h>
#include <TH2Poly.h>
#include <TFile.h>
#include <TF1.h>
#include <TArrow.h>
#include <TBox.h>
#include <TTree.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TString.h>
#include <TEllipse.h>
#include <TSystem.h>
#include <TGraphErrors.h>
#include <iostream>
#include <cmath>
#include <fstream>
#include "crystalpos.h"

using namespace std;

#define pi_greco 3.14159265359

#define NCRYMAX 2000
#define NCLUMAX 100
#define NVDMAX 100

#define nCORNERs 4

#define ECRYMIN 15.

#define nDISKs 2

#define NSEEDMAX 100

#define PMIN 90.
#define MAXNVDGOOD 100
#define MAXNCLUGOOD 100

#define nTHBINs 70
#define nRHOBINs 70

#define NMUHITMAX 10

#define MVACUT 0.

#define DEBUG true

void evdisplay_plot(TString filename = "Cosmic_dataset")
{

  cout.setf(ios::fixed);
  cout.precision(1);

  float wcry;
  wcry = xcry[1] - xcry[0];
  float xmin0, xmax0;
  xmin0 = -20. * wcry;
  xmax0 = 20. * wcry;
  float RHOMIN, RHOMAX;
  RHOMIN = xmin0;
  RHOMAX = xmax0;

  char hname[100];
  char htitle[200];

  float ymin = 2000;
  float xmin = 2000;
  float ylayer[37];

  for (int icry = 0; icry < 674; icry++)
  {
    if (ycry[icry] <= ymin)
    {
      ymin = ycry[icry];
    }
  }

  for (int ilay = 0; ilay < 37; ilay++)
  {
    ylayer[ilay] = ymin + ilay * 34.3;
  }

  struct CaloGeoCable
  {
    int kind;     // 0 = CsI, 1=LaBr, 2 =PinDiode
    int cryId;    // 0-1347 for Csi/Labr, 1348-1355 for PD
    int boardPoi; //
    int chanNum;  //
    int indX;     //
    int indY;
    float xpos;
    float ypos;
  };

  struct CaloGeoCable CaloCable[1356];
  // struct Daq2CaloID[1356];

  int NumXval[37] = {};
  float XminVal[37] = {};
  float XposVal[37][30] = {};
  float XposValOrdered[37][30] = {};
  int numcur = 0;

  for (int icry = 0; icry < 674; icry++)
  {
    for (int ilay = 0; ilay < 37; ilay++)
    {
      if (ycry[icry] > ylayer[ilay] - 10 && ycry[icry] < ylayer[ilay] + 10)
      {
        numcur = NumXval[ilay];
        XposVal[ilay][numcur] = xcry[icry];
        NumXval[ilay] = NumXval[ilay] + 1;
        //	if( xcry[icry]<= XminVal[ilay]) {
        //  XminVal[ilay] = xcry[icry];
        //}
      }
    }
  }

  //
  // now order XposVal from minimum to maximum
  //

  for (int ilay = 0; ilay < 37; ilay++)
  {
    int numval = NumXval[ilay];
    vector<float> xtest(numval);
    vector<int> xpointer(numval);
    for (int ix = 0; ix < NumXval[ilay]; ix++)
    {
      xtest[ix] = XposVal[ilay][ix];
      xpointer[ix] = ix;
      //      cout << " ilay " << ilay << " ix " << ix << " Xval  " << xtest[ix] << endl;
    }
    sort(xpointer.begin(), xpointer.end(), [&](int i, int j)
         { return xtest[i] < xtest[j]; });
    for (int ix = 0; ix < NumXval[ilay]; ix++)
    {
      int inew = xpointer[ix];
      XposValOrdered[ilay][ix] = xtest[inew];
      // cout << " ilay " << ilay << " ix " << ix << " Xval" << xtest[ix] << " Xpointer " << xtest[inew] << endl;
    }
  }

  //
  // Fill part of structure CaloCable .. organized by cryid
  // once check it out create new structure organized by daqid
  //

  float xcurrent;
  for (int icry = 0; icry < 674; icry++)
  {
    for (int ilay = 0; ilay < 37; ilay++)
    {
      if (ycry[icry] > ylayer[ilay] - 10 && ycry[icry] < ylayer[ilay] + 10)
      {
        for (int ix = 0; ix < NumXval[ilay]; ix++)
        {
          xcurrent = XposValOrdered[ilay][ix];
          if (xcry[icry] > xcurrent - 10 && xcry[icry] < xcurrent + 10)
          {
            CaloCable[icry].cryId = icry;
            CaloCable[icry].indX = ix;
            CaloCable[icry].indY = ilay;
            CaloCable[icry].xpos = xcry[icry];
            CaloCable[icry].ypos = ycry[icry];
          }
        }
      }
    }
  }

  ifstream in;
  in.open("Crystal4-map.dat");
  int ipoi, dk, chan, phi, crate, board, sensor, ind_x, ind_y;
  for (int calpoi = 0; calpoi < 1348; calpoi++)
  {
    dk = 0;
    in >> ipoi >> phi >> crate >> board >> sensor >> chan >> ind_x >> ind_y;
    for (int icry = 0; icry < 674; icry++)
    {
      int cryval = CaloCable[icry].cryId;
      int indxx = CaloCable[icry].indX;
      int indyy = CaloCable[icry].indY;
      if (ind_x == indxx && ind_y == indyy)
      {

        printf("%d %d %d %d %d %d %d %d %d %d %.2f %.2f \n", ipoi, dk, chan, phi, crate, board, sensor, ind_x, ind_y, cryval);
      }
    }
    // cout << ipoi << " " << disk <<" " << chan << phi << crate << board << sensor << x < y << endl;
  }
  in.close();

}

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <utility>
#include <algorithm>
#include "ReaderDmap.h"

using namespace std;

ReaderDmap::ReaderDmap(string filename) : _BoardNum(300), _selIdx(-1) {

	m_addr = new string[_BoardNum];
	_BoardPOIArr = new int[_BoardNum];
	_CablingArr = new Cabling[_BoardNum];
	_DtcIDArr = new DtcID[_BoardNum];

    ReadFile(filename);
}

ReaderDmap::~ReaderDmap() {
	delete [] m_addr;
	delete [] _BoardPOIArr;
	delete [] _CablingArr;
	delete [] _DtcIDArr;
}

void ReaderDmap::ReadFile(string &fileName){
    ifstream file;
    file.open(fileName.c_str());
    int counter;

    int BoardID[674][2]; // from Crystal-ID to BoardNum Sensor 0/1
    int BoardNum;      // Phi*40+Crate*8+Board*2+Sensor
    int Daqid2Cryid[1348]; // from Daqid to Cryid for Sensor 0

    //int X, Y, Disk, Phi, Crate, Board, Sensor, Height, Row, Loc, dum1, dum2, dum3;
    int daqid, disk, chan, phi, crate, board, sensor, Ix, Iy, CryId;

    for(int j=0;j<674;j++){
      BoardID[j][0] = 0;
      BoardID[j][1] = 0;
    }

    for(int CryId=0; CryId< 1348; CryId++){
      //cout << CryId << " " << BoardID[CryId][0] << " " << BoardID[CryId][1] << endl; 
    }
    cout << "#==========================================================" << endl;
    cout << "# Calorimeter DMAP version 0.9, 31-March-2020 "<< endl;
    cout << "# Authors: S.Miscetti, D.Pasciuto" << endl;
    cout << "#===========================================================" << endl;
    cout << "#Calpoi-Disk-PhiD-Crate-Board-Sensor-Chan-IXnum-IYnum-CryId" << endl;
    cout << "#===========================================================" << endl;
    int row = 0;
    while (!file.eof()) {

    	   std::string str;
    	   std::getline(file, str);
    	   if(str[0] == '#') continue; //skip comment
    	   std::stringstream ss(str);
    	   ss >> daqid >> disk >> chan >> phi >> crate >> board >> sensor >> Ix >> Iy >> CryId;
	   BoardNum = phi*40 + crate*8+board*2+sensor;
	   //if( BoardNum>80 )cout << " Board# " << BoardNum << " " <<  phi << " " << crate << " " << board << " " << sensor << endl;

	   if(1){
	     printf(" %*d  %*d  %*d  %*d %*d %*d  %*d %*d %*d %*d \n",3,daqid, 3,disk,3,phi, 4,crate, 5,board, 5,sensor, 5,chan, 5,Ix, 5,Iy, 5,CryId);
	     // cout  << daqid << " " <<  CryId << " " << BoardNum << " " << sensor << endl;
	      if( sensor == 0) Daqid2Cryid[daqid] = CryId;
	       BoardID[CryId][sensor]=BoardNum;
	   }
    	   row++;
	    
    }

   file.close();

   for(int id=0; id< 1348; id++){
     cout << " " << id << " " << BoardID[id][0] << " " << BoardID[id][1] << endl; 
   }
}

pair<double,double> ReaderDmap::GetData(string address){

//uso address per chiamare la board

pair<double,double> coppia;
double volt = 50;
double temp = 20;
coppia.first = volt;
coppia.second = temp;

return coppia;

}

double ReaderDmap::SetData(string address, double Voltin){

//uso address per chiamare la board

double voltout;

voltout = Voltin*0.9;


return voltout;

}

string ReaderDmap::GetAddress(int num){

return m_addr[num];

}

int ReaderDmap::GetPointCol(int row, int col){

return 0;//m_pointcol[row][col];

}

void ReaderDmap::SelByBoardID(int boardId) {
	_selIdx = (find(_BoardPOIArr,_BoardPOIArr+_BoardNum,boardId)-_BoardPOIArr);
}

void ReaderDmap::SelByCabling(bool DiskN, bool CrateSide, int Crate, int CrateSlot, bool BoardSide) {
	_selIdx = (find(_CablingArr,_CablingArr+_BoardNum,Cabling(DiskN,CrateSide,Crate,CrateSlot,BoardSide))-_CablingArr);
}


void ReaderDmap::SelByDtc(int dtcn, int fiber) {
	_selIdx = (find(_DtcIDArr,_DtcIDArr+_BoardNum,make_pair(dtcn,fiber))-_DtcIDArr);
}

int ReaderDmap::GetSelBoardPOI() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return -1;
	}
	return _BoardPOIArr[_selIdx];
}

Cabling ReaderDmap::GetSelCabling() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return Cabling();
	}
	return _CablingArr[_selIdx];
}

DtcID ReaderDmap::GetSelDtc() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return make_pair(-1,-1);
	}
	return _DtcIDArr[_selIdx];
}



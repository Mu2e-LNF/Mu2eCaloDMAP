#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <utility>
#include <algorithm>
#include "ReaderChannel.h"

using namespace std;

ReaderChannel::ReaderChannel(string filename) : _BoardNum(300), _selIdx(-1) {

	m_addr = new string[_BoardNum];
	_BoardPOIArr = new int[_BoardNum];
	_CablingArr = new Cabling[_BoardNum];
	_DtcIDArr = new DtcID[_BoardNum];

    ReadFile(filename);
}

ReaderChannel::~ReaderChannel() {
	delete [] m_addr;
	delete [] _BoardPOIArr;
	delete [] _CablingArr;
	delete [] _DtcIDArr;
}
void ReaderChannel::ReadFile(string &fileName){
    ifstream file;
    file.open(fileName.c_str());
    int counter;

    int X, Y, Disk, Phi, Crate, Board, Sensor, Height, Row, Loc, dum1, dum2, dum3;
   
    int row = 0;
    while (!file.eof()) {
      
    	   std::string str;
    	   std::getline(file, str);
	   //cout << " PIPPO " << str << endl;
    	   if(str[0] == '#') continue; //skip comment
    	   std::stringstream ss(str);
    	   ss >> X >> Y >> Phi >> Crate >> Board >> Sensor >> Height >> Row >> Loc >> dum1 >> dum2 >> dum3;
	   //cout << " X " << X << " Y " << Y << endl;
	   int channelnum=0;
	   if( Height==0) channelnum = Row*4+Loc;
	   if( Height==1) channelnum = 8+Loc;
	   if( Height==2) channelnum = 12+ Row*4+Loc;
			
	   if( row< 1348){
	     cout  << row <<  " " << Phi << " " <<  Crate << " " <<  Board << " " << Sensor << " " << channelnum << " " <<    X << "  " << Y << endl;
	   }
    	   row++;
	    
    }


   file.close();

}

pair<double,double> ReaderChannel::GetData(string address){

//uso address per chiamare la board

pair<double,double> coppia;
double volt = 50;
double temp = 20;
coppia.first = volt;
coppia.second = temp;

return coppia;

}

double ReaderChannel::SetData(string address, double Voltin){

//uso address per chiamare la board

double voltout;

voltout = Voltin*0.9;


return voltout;

}

string ReaderChannel::GetAddress(int num){

return m_addr[num];

}

int ReaderChannel::GetPointCol(int row, int col){

return 0;//m_pointcol[row][col];

}

void ReaderChannel::SelByBoardID(int boardId) {
	_selIdx = (find(_BoardPOIArr,_BoardPOIArr+_BoardNum,boardId)-_BoardPOIArr);
}

void ReaderChannel::SelByCabling(bool DiskN, bool CrateSide, int Crate, int CrateSlot, bool BoardSide) {
	_selIdx = (find(_CablingArr,_CablingArr+_BoardNum,Cabling(DiskN,CrateSide,Crate,CrateSlot,BoardSide))-_CablingArr);
}


void ReaderChannel::SelByDtc(int dtcn, int fiber) {
	_selIdx = (find(_DtcIDArr,_DtcIDArr+_BoardNum,make_pair(dtcn,fiber))-_DtcIDArr);
}

int ReaderChannel::GetSelBoardPOI() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return -1;
	}
	return _BoardPOIArr[_selIdx];
}

Cabling ReaderChannel::GetSelCabling() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return Cabling();
	}
	return _CablingArr[_selIdx];
}

DtcID ReaderChannel::GetSelDtc() {
	if (_selIdx==-1) {
		cerr<<"Selection not yet done! Returing fake value"<<endl;
		return make_pair(-1,-1);
	}
	return _DtcIDArr[_selIdx];
}



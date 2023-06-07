#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <utility>

using namespace std;

struct Cabling {
	Cabling() : DiskN(false), CrateSide(false), Crate(-1), CrateSlot(-1), BoardSide(false) {}
	Cabling(bool diskN, bool crateSide, int crate, int crateSlot, bool boardSide) :
		DiskN(diskN), CrateSide(crateSide), Crate(crate), CrateSlot(crateSlot), BoardSide(boardSide) {}
	bool DiskN;
	bool CrateSide;
	int  Crate;
	int  CrateSlot;
	bool BoardSide;

	bool operator==(const Cabling& cbl) const{
		return (DiskN == cbl.DiskN && CrateSide == cbl.CrateSide && Crate==cbl.Crate && CrateSlot==cbl.CrateSlot && BoardSide==cbl.BoardSide);
	}

};
inline std::ostream& operator<<(std::ostream& os, const Cabling& obj)
{
    os<<obj.DiskN <<" "<< obj.CrateSide <<" "<< obj.Crate <<" "<< obj.CrateSlot <<" "<< obj.BoardSide;
    return os;
}
//	std::istream& operator>>(std::istream& is, Cabling& obj)
//	{
//	    // read obj from stream
//	    if( /* T could not be constructed */ )
//	        is.setstate(std::ios::failbit);
//	    return is;
//	}

typedef pair<int,int> DtcID;
inline std::ostream& operator<<(std::ostream& os, const DtcID& obj)
{
    os<<obj.first <<" "<< obj.second;
    return os;
}

class ReaderChannel
{

  public:
   ReaderChannel(string filename);
   ~ReaderChannel();

   void ReadFile(string &fileName);

   pair<double,double> GetData(string address);

   double SetData(string address, double Voltin);

   string GetAddress(int num);

   int GetPointCol(int row, int col);

   void SelByBoardID(int boardId);
   void SelByCabling(bool DiskN, bool CrateSide, int Crate, int CrateSlot, bool BoardSide);
   void SelByDtc(int dtcn, int fiber);

   int GetSelIdx() { return _selIdx; }
   int GetSelBoardPOI();
   Cabling GetSelCabling();
   DtcID GetSelDtc();

  private:
   int _BoardNum;
   string *m_addr;
   //int **m_pointcol;

   int *_BoardPOIArr;
   Cabling *_CablingArr;
   DtcID *_DtcIDArr;

   int _selIdx;

};

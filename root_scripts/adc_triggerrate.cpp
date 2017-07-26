#include "CreamFile.h"
#include "CreamCAL.h"
#include "timez.h"

#include </usr/local/root/include/TROOT.h>
#include </usr/local/root/include/TFile.h>
#include </usr/local/root/include/TTree.h>
#include <cstdlib>

#include <iostream>
using namespace std;
#include <string>
#include <cstdlib>

// ROOT Headers
#include "TApplication.h"
#include "TTimeStamp.h"
#include "TCanvas.h"
#include "TROOT.h"
#include "TTree.h"
#include "TFile.h"
#include "TArc.h"
#include "TH1.h"
#include "TSystem.h"

TFile *fout;
TTree *tree;

struct evtroot {
public:
	unsigned	evt;
        unsigned        time[6];
	unsigned	trig[9];

        struct {
                unsigned adc[2560];
        } cal;
} sevt;

std::string ExtractFilename( const std::string& path )
{
	return path.substr( path.find_last_of( '/' ) +1 );
}

std::string ChangeExtension( const std::string& path, const std::string& ext )
{
	std::string filename = ExtractFilename( path );
	return filename.substr( 0, filename.find_last_of( '.' ) ) +ext;
}

void process (CreamFile& cfile)
	{
	unsigned  nevent;
        unsigned  TimeStamp[6];

	DEvent    ev;
	unsigned  i;

	CreamCAL cal;
          
	for(nevent = 1; ; nevent++) {
		/* clear event data */
		ev.Clear();

		/* read an event */
		if ( cfile.ReadEvent( ev ) == -1 ) break;

		cal.Run(ev);

		sevt.evt = nevent;		
		ev.GetTimeStamp(&TimeStamp[0]) ;

                sevt.trig[0]= ev.TriggerQ();
                sevt.trig[1]= ev.CalibrationTriggerQ();
                sevt.trig[2]= ev.ExternalTriggerQ();
                sevt.trig[3]= ev.CalorimeterTriggerQ();
                sevt.trig[4]= ev.CDTRG1TriggerQ();
                sevt.trig[5]= ev.CDTRG2TriggerQ();
                sevt.trig[6]= ev.ZCalibrationTriggerQ();
		sevt.trig[7]= ev.EHiTriggerQ();
                sevt.trig[8]= ev.ELowTriggerQ();

                for (i=0;i<2560;i++)
                       sevt.cal.adc[i]=cal.GetADC(i);

		tree->Fill();                       
	} // for nevent;
}

void do_file()
	{
	CreamFile cfile;

        char  filename[100];
	char cbuf[256];
	string   fpath ;
	string   rfile ;
	string   wfile ;

	fpath += "./LIST" ;
	FILE *fin ;
	fin = fopen(fpath.c_str(),"r") ;

	if ( fin == 0 ) {
	      cerr << "cannot open file " << fpath << endl;
	      exit( 1 );
	}

	while ( fgets(cbuf, 256, fin) != 0 ) {
	  if ( cbuf[0] == '#' ) continue; // skip comment lines
	  sscanf(cbuf,"%s\n",filename) ;	

		wfile= "./ROOT/";
		wfile+= ChangeExtension (filename, ".root");
	        fout = new TFile(wfile.c_str(),"RECREATE") ;
	        tree = new TTree("event","EVENT") ;

		tree->Branch("evt",&sevt.evt,"evt/i") ;
		tree->Branch("time",&sevt.time,"time[6]/i") ;
		tree->Branch("trig",&sevt.trig,"trig[9]/i") ;
		tree->Branch("cal",&sevt.cal,"adc[2560]/i") ;

		cout <<filename<<" is reading...\n";
		if ( cfile.Open( filename ) == 0 ) {
			process ( cfile);
                        cfile.Close();
		}
		else
			fprintf(stderr, "ERROR: cannot open file %s\n", filename);

	        fout->Write() ;
	        fout->Close() ;
		cout <<wfile<<" is generated...\n";
	} //while
}

int main()
	{

	do_file( );

	return 0;
}

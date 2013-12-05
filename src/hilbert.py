#!/usr/bin/python
"""
In this stage, we read the Database (using correlated index) and 
evalute the Hilbert index for each IP addresses
"""
import sys, os, time, struct, subprocess
import signal
from optparse import OptionParser

# CUSTOM LIBRARY

from dbindex import *
from common import *

# from libhilbert import gray_encode_travel, gray_decode_travel, child_start_end
from libhilbert import int_to_Hilbert, Hilbert_to_int

class tool:
    def __init__(self, options):   
        self.option = options

        if self.option['nf_input_dir'] == None: sys.exit("Input error")
        if self.option['nf_output_dir'] == None: sys.exit("Output error")


        if not os.path.exists( self.option['nf_input_dir']): 
            sys.exit("Input error")

        self.util = nfcommon()

        # INPUT 
        self.statdb_file        = open( self.option['nf_input_dir'] ,'r+b')
        self.nf_index           =  simpleindex( self.option['nf_input_dir'] + ".idx" )
        self.nf_index.load_index()
        # print self.nf_index.get_seek_by_index([1,1,168,192])
        # raw_input()

        # OUTPUT
        self.hilbertfilename    = self.option['nf_output_dir'] 
        self.outfile            = open( self.hilbertfilename, 'w')

    def close(self):
        self.outfile.close()

    def debug(self, msg):
        print "[MAIN] ", msg

    def write_hindex(self, ip, hilbert):
        # ip_int = int(self.util.ip2int(ip))
        # write binary output
        # self.outfile.write( struct.pack(self.structindexformat, ip_int  , hilbert) )

        # write ASCII output
        pass
    

    def hilbert(self):

        c = 0 

        print "Scanning index file"
        for i in range(0,256):
            for j in range(0,256):
                for t in self.nf_index.get_ips_by_index([i,j]):
                    for q in self.nf_index.get_ips_by_index([i,j,t]):

                        c += 1
                        ips = str(q)+"."+str(t)+"."+str(j)+"."+str(i)
                        seek = self.nf_index.get_seek_by_index([i,j,t,q])

                        seek = self.nf_index.get_ips_by_index([i,j,t,q])

                        # print "IP",ips," S->",seek

                        if seek  == None: sys.exit( "[" +str(  (i,j,t,q) )+  "] Seek non trovato" )


                        self.statdb_file.seek( seek )

                        value = self.statdb_file.read( self.util.getdatasize() )

                        data = self.util.bin2data( value )

                        pt = [ int(data['bm']),int(data['bd']),  
                                        int(data['pm']), int(data['pd']),
                                        int(data['bppm']),int(data['bppd']),
                                        int(data['ppsm']),int(data['ppsd']),
                                        int(data['bpsm']),int(data['bpsd']),
                                ]

                        x = Hilbert_to_int( pt )

                        # print "(seek",seek,") PT", pt ,"->",x   
                        # raw_input()
        
                        # Use write_hindex if you need binary writing
                        self.outfile.write( str(ips)+" "+ str(x) + "\n")
                        # print ips, " ", x
                        del x; del pt; del ips;

        print "Processati ",c ," IP"
        
        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input-file", dest="nf_input_dir", default=None, help="input file")
    parser.add_option("-o", "--output-file", dest="nf_output_dir", default=None, help="output file")
    (options, args) = parser.parse_args()
    
    a = tool(options.__dict__)
    a.hilbert()
    a.close()




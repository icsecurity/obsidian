#!/usr/bin/python

"""
please readme the README file to know about the software 
workflows and the LICENCE file for licence informations.
"""

# import system library
import sys, os, signal, time
from optparse import OptionParser
from struct import *

# CUSTUM LIBRARY 
from nfutils import *
from nf_merger import *

import threading

""" THREAT WORKER """
class nffileProcess( threading.Thread ):
    def __init__(self, lock, tname, nffile, merger):
        threading.Thread.__init__(self)
        self.name       = tname
        self.nffile     = nffile
        self.nf_counter = 0 

        self.lock       = lock # Sincronizza i thread

        self.dataformat = "QQQIcccIIHHxxxx"             # data file format (nfStat results)
        self.size       = calcsize(self.dataformat)

        self.util       = nf_utils( "" )
        self.db         = {}
        self.merger     = merger

    def get_record(self, ret):
        (flussi,bytes,packets,duration,flag,proto,tos,srcip,dstip,srcport,dstport) = unpack(self.dataformat, ret)
        ret = {'flussi': flussi, 'bytes': bytes, 'packets': packets, 'duration': duration, 'flag': flag, 'proto': proto, 
                'tos': tos, 'srcip': srcip, 'dstip': dstip,  'srcport': srcport, 'dstport': dstport}
        return ret

    def add_db(self, ips, content):
        if not self.db.has_key( ips ):
            # Initialize db entry
            self.db[ ips ] = {}
            self.db[ ips ]["counter"] = 0
            self.db[ ips ]["ba"]      = 0
            self.db[ ips ]["ba2"]     = 0
            self.db[ ips ]["pa"]      = 0
            self.db[ ips ]["pa2"]     = 0
            self.db[ ips ]["ppsa"]    = 0
            self.db[ ips ]["ppsa2"]   = 0
            self.db[ ips ]["bpsa"]    = 0
            self.db[ ips ]["bpsa2"]   = 0
            self.db[ ips ]["bppa"]    = 0
            self.db[ ips ]["bppa2"]   = 0

        # Update values

        pps = float(content['packets']) / float(content['duration'])
        bps = float(content['bytes']) / float(content['duration'])
        bpp = float(content['bytes']) / float(content['packets'])

        self.db[ ips ]["counter"] += 1
        self.db[ ips ]["ba"]      += int(content['bytes'])
        self.db[ ips ]["ba2"]     += ( int(content['bytes']) * int(content['bytes']) )
        self.db[ ips ]["pa"]      += int(content['packets'])
        self.db[ ips ]["pa2"]     += ( int(content['packets']) * int(content['packets']) )
        self.db[ ips ]["ppsa"]    += pps
        self.db[ ips ]["ppsa2"]   += ( pps * pps)
        self.db[ ips ]["bpsa"]    += bps
        self.db[ ips ]["bpsa2"]   += ( bps * bps )
        self.db[ ips ]["bppa"]    += bpp
        self.db[ ips ]["bppa2"]   += ( bpp * bpp )
        return 

    """ THREAT MAIN """
    def run(self):
        # load file (all) in memory 
        filesize = os.path.getsize( self.nffile )
        f = open(self.nffile, 'r')
        filecontent = f.read( filesize ) # carico tutto il file in memoria
        f.close

        print "[T-"+str(self.name)+"] File " + str(self.nffile) + " ("+ str(filesize/self.size) +" rec.) started."
        f_index = 0 
        while True:
            ret =  filecontent[ int( f_index * self.size ): int((f_index+1) * self.size) ]
            if ret == "": break
            f_index += 1 ; self.nf_counter += 1

            r = self.get_record( ret ) 

            srcip = self.util.int2ip(r['srcip'])
            dstip = self.util.int2ip(r['dstip']) 

            self.add_db( srcip, r )
            self.add_db( dstip, r )

            del r
 
        # merge database 
        self.merger.merge( self.db )
        print "[T-"+str(self.name)+"] File " + str(self.nffile) + " letti ", self.nf_counter,"records."

        # release resources (and other threads to work)
        del filecontent
        del self.db
        self.lock.release()

""" GENERIC CLASS FOR MAIN PROCESS """
class tool:
    def __init__(self, options):   

        self.debug_mode = False
        self.option     = options       # input options

        if self.option['nf_input_dir'] == None or not os.path.isdir(self.option['nf_input_dir']):
            sys.exit("Input dir ("+str(self.option['nf_input_dir'])+") is not a valid dir.")

        self.maxproc    = self.option['threat']                        # max number of thread
        self.mylock     = threading.BoundedSemaphore( self.maxproc )   # threads sync semaphore

        self.util       = nf_utils( options )
        self.merger     = nf_merger( self.option['nf_output_dir'] )

        if self.debug:
            self.debug("Main Input options:" + str(options) ) 

    def debug(self, msg):
        if self.debug_mode: print "[MAIN] ", msg

    """ MAIN """
    def run(self):
        listing = os.listdir( self.option['nf_input_dir'] )
        listing.sort(reverse=True)

        # finish_sem = threading.BoundedSemaphore( len( listing ) )

        self.debug("Found "+ str(len( listing )) + " files." )
        self.debug("Making DB ... ")

        tlist = []          # list of pending threads

        for f in listing:   

            # waiting semaphore and launch the nffileProcess process - pool control
            self.mylock.acquire()
            a = nffileProcess( self.mylock, str(c), self.option['nf_input_dir'] + "/" + f, self.merger ) 
            tlist.append( a )
            a.start()

        for a in tlist: # waiting for all the threads
            a.join()

        # dump data DB and Index 
        self.merger.dump2files() 

        # close resources 
        self.merger.close() 

if __name__ == "__main__":

    # parse the input parameters
    parser = OptionParser()
    parser.add_option("-d", "--dir",    dest="nf_input_dir", default=None, help="input dir")
    parser.add_option("-t", "--threat", dest="threat", type=int, default=None, help="Threats number")
    parser.add_option("-o", "--output", dest="nf_output_dir", default=None, help="output dir")
    (options, args) = parser.parse_args()

    w = tool(options.__dict__)
    w.run()


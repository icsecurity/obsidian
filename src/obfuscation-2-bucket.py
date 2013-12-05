#!/usr/bin/python

"""
Please refer to LICENCE FILE
Domenio Vitali - vitali@di.uniroma1.it, domenico.vitali@gmail.com
"""

import sys, os, math
from optparse import OptionParser
from sets import Set
from collections import deque # per gestire i file aperti per la scrittura

class tool:

    def __init__(self, options):   
        self.option                 = options               # INPUT options

        if self.option['j'] == None: sys.exit("J missing")
        if self.option['input_dir'] == None: sys.exit("Input dir missing")
        if self.option['output_dir'] == None: sys.exit("Output dir missing")

        if not os.path.isdir( self.option['input_dir']): sys.exit("Input dir error")
        if not os.path.isdir( self.option['output_dir']): sys.exit("Output dir error")
        if self.option['j'] < 2: sys.exit("Error: J < 2")

        self.j            = self.option['j']      # INPUT parameter
        self.outfiles     = {}
        self.flowsapp     = {}
        self.outfilequeue = deque([]) # la coda contiene i nomi dei file, ovvero gli indici del DICT
        self.maxqueuelen  = 2
 
    def run(self):

        # we get time-ordered list of files
        listing = os.listdir( self.option['input_dir'] )
        listing.sort() 

        for infile in listing: # for each files            
            print "Reading file: ", infile
            ffile = open( self.option['input_dir']  + "/" + infile, 'r')
            content = ffile.read() # carico tutto il file in memoria
            lines = content.split("\n")
            ffile.close(); del ffile; del content

            for line in lines:

                # empty lines ?
                if line == "" or line == None or line[0] == "#": 
                    continue
                
                # outfile.write("# ORIGFNAME INDEX SRCIP SRCPORT DSTIP DSTPORT PROTO FLAG TOS BYTES PACKETS DURATIONS \n")
                r = {}
                t = line.split()

                r['filename']   = t[0]
                r['flowindex']  = t[1]
                r['srcip']      = str( t[2] )
                r['srcport']    = int( t[3] )
                r['dstip']      = str( t[4] )
                r['dstport']    = int( t[5] )
                r['proto']      = t[6]
                r['flag']       = t[7]
                r['tos']        = int( t[8] )
                r['byte']       = int( t[9] )
                r['packet']     = int( t[10] )
                r['duration']   = int( t[11] )
                r['hilbert']    = t[12]

                del t
                
                # Add record to flowsapp structure
                if not self.flowsapp.has_key( r['srcip'] ):
                    self.flowsapp[ r['srcip'] ] = []
                self.flowsapp[ r['srcip'] ].append( r )

                if len( self.flowsapp[ r['srcip'] ] ) > (self.option['j'] - 1):
                    self.writeout( self.flowsapp[ r['srcip'] ] ) # LISTA DI RECORDs 
                    del self.flowsapp[ r['srcip'] ]


        self.closeallfile()

    """ Close All Output File Sockets """ 
    def closeallfile(self):
        # Close all opened files
        for i in self.outfiles: self.outfiles[i].close()
            
    """ Convert a Single Record in a string """
    def records2string(self, r, bytes, packets, flags, tos, proto):
        # ORIGFNAME INDEX SRCIP SRCPORT DSTIP DSTPORT PROTO FLAG TOS BYTES PACKETS DURATIONS
        outstr = str(r['flowindex'])+" "+str(r['srcip'])+" "+str(r['srcport'])+" "+str(r['dstip'])+" "+str(r['dstport'])
        outstr = outstr+" "+str(list(proto)).replace(" ","")+" "+str(list(flags)).replace(" ","")+" "+str(list(tos)).replace(" ","")+" "
        # per i set
        # outstr = outstr+str(list(bytes)).replace(" ","")+" "+str(list(packets)).replace(" ","")+" "+str(r['duration'])
        outstr = outstr+str(bytes).replace(" ","")+" "+str(packets).replace(" ","")+" "+str(r['duration'])
        return outstr

    """ write a set of records into files """
    def writeout(self, rs):

        flags   = Set([])
        tos     = Set([])
        proto   = Set([])
        # bytes   = Set([])
        # packets = Set([])
        bytes   = []
        packets = []

        for r in rs:

            # bytes   |= Set([ r['byte'] ])
            # packets |= Set([ r['packet'] ])
            bytes.append( r['byte'] )
            packets.append( r['packet'] )
            
            flags   |= Set([ r['flag'] ])
            tos     |= Set([ r['tos'] ])
            proto   |= Set([ r['proto'] ])

        # Accodo tutte le stringhe
        outstr = ""
        for r in rs:        
            outstr = outstr + self.records2string( r, bytes, packets, flags, tos, proto ) + "\n"

        del bytes, packets, flags, tos, proto

        # questo e' un'errore ... perhce' ogni flusso va riscritto nel suo file 
        # invece qui prendo un file e lo metto tutti insieme da una parte 
        # print outstr
        # WRITE ON FILE QUALE FILE ????s
        if not self.outfiles.has_key( r['filename'] ):
            self.openfile( r['filename'] )

        # print "outfiles" , self.outfiles
        # print " FILE -> ", self.outfiles[ r['filename'] ]
        # print "outfiles" , self.outfiles
        self.outfiles[ r['filename'] ].write( outstr )
        del outstr

    def openfile(self, filename):
        self.outfilequeue.append( filename )
        self.outfiles[ filename ] = open( self.option['output_dir'] + "/"+ filename,  'a')
        # print "QUIII" , self.outfiles[ filename ]
        if len( self.outfilequeue ) > self.maxqueuelen:
            filetoclose = self.outfilequeue.popleft()
            # print "CHIUDO FILE ", filetoclose
            self.outfiles[ filetoclose ].close()
            del self.outfiles[ filetoclose ]
        # print "outfiles" , self.outfiles


###### MAIN ###### 
if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-d", "--dir",            dest="input_dir", default=None, help="input dir")
    parser.add_option("-o", "--output-file",    dest="output_dir", default=None, help="output dir")
    parser.add_option("-j", "--j-value",        dest="j", default=0, type=int, help="output dir")

    (options, args) = parser.parse_args()
        
    # This script realize the Obfuscation J funciont. It 
    # assumes to work with SORTED by FLOWS Hilbert index
    a = tool(options.__dict__)
    a.run()

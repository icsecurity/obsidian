#!/usr/bin/python

""" 
Questo script prende in INPUT un file (ORDINATO) contenente gli IP e il 
valore di HILBERT ASSOCIATO e CREA I GRUPPI DI K ELEMENTI.
"""

import sys, os, signal, time
from optparse import OptionParser

class tool:
    def __init__(self, option):
        self.option     = option
        print option
        self.f              = open(self.option['hilbertfile'], 'r' )
        self.outf           = open(self.option['outputfile'], 'w')
        self.lastgroup      = None
        self.previousgroup  = None
        self.previous_buff  = ""
        self.buff           = ""       
        self.check()

    def check(self):
        if self.option['outputfile'] == None: sys.exit("No output file")
        if self.option['hilbertfile'] == None: sys.exit("No Hilbert file error")
        if not os.path.isfile( self.option['hilbertfile'] ): sys.exit( "Hilbert file error" )
        if self.option['k'] == 0: sys.exit( "K must be != 0" )

    def run(self):
        print "Grouping IP .." 

        buff        = []
        lastrand    = ""

        while True:

            line = self.f.readline() 
            if line == "": del line; break                
            (ip,h) = line.split()

            buff.append( str(ip) )

            if len(buff) == self.option['k']:
                lastrand = buff[0]
                for ip in buff:
                    self.outf.write( lastrand + " " + ip + "\n")
                buff = []

            del line; del ip; del h;

        if len(buff) > 0:
            for ip in buff:
                self.outf.write( lastrand + " " + ip + "\n")

    def close(self):
        self.f.close()
        self.outf.close()

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-f", "--hilbert-file", dest="hilbertfile", default=None, help="(input) hilbert file")
    parser.add_option("-o", "--output-file", dest="outputfile", default=None, help="output IP group file ")
    parser.add_option("-k", "--kappa", dest="k", default=0, type=int, help="minimum group cardinality")

    (options, args) = parser.parse_args()

    a = tool(options.__dict__)
    a.run()

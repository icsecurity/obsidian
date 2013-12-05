#!/usr/bin/python
"""
This software creates ASCII files and replace each source and destination IP addresses 
with the obfuscated verion. It requires, as input, the original dataset and the GroupIP
file.
"""

import sys, os, struct
from optparse import OptionParser

import random
import threading

from nfutils import *
from libhilbert import int_to_Hilbert, Hilbert_to_int

class SortedInputFile:
    def __init__(self, infile):
        self.infile             = open( infile , 'r+b')
        self.bufferfile         = self.infile.read()
        self.db_record_format   = "QQQIcccIIHHxxxx"
        self.db_record_size     = struct.calcsize(self.db_record_format)
        self.record_count       = os.path.getsize( infile ) / self.db_record_size
        self.counter            = 0 

    def getname(self):  
        return self.infile.name 

    def close(self):    
        self.infile.close()

    def getCount( self ):
        return self.record_count 

    def get_record(self, _index):
        if _index > self.record_count:
            return "" # OUT OF FILE
        # seek file for record _index
        index = _index * self.db_record_size
        ret = self.bufferfile[index:index+self.db_record_size] # record = f.read( self.db_record_size ) 
        (flussi,bytes,packets,duration,flag,proto,tos,srcip,dstip,srcport,dstport) = struct.unpack(self.db_record_format, ret)
        # return a dict of data 
        return {'flussi': flussi, 'bytes': bytes, 'packets': packets, 'duration': duration, 'flag': flag, 'proto': proto, 
                'tos': tos, 'srcip': srcip, 'dstip': dstip,  'srcport': srcport, 'dstport': dstport}

class nffileProcess( threading.Thread ):

    def __init__(self, lock, tname, inputfilepath, outputfilepath, i_gip):
        threading.Thread.__init__(self)

        self.mylock = lock # pool controller 
        self.inputfilepath = inputfilepath
        self.outputfilepath = outputfilepath
        self.i_gip = i_gip
        self.utils = nf_utils()

        self.infile = SortedInputFile( self.inputfilepath )
        self.outfile = open( self.outputfilepath, 'w')
        self.flow_counter = 0     
    
    def run(self):
        # output header
        self.outfile.write("# ORIGFNAME INDEX SRCIP SRCPORT DSTIP DSTPORT PROTO FLAG TOS BYTES PACKETS DURATIONS \n")

        fname = os.path.basename( self.infile.getname() )
        print "Reading file ("+ fname +"): ", self.infile

        for i in range( self.infile.getCount() ): # for all record
            self.flow_counter   += 1 # self.flow_counter has been initialized to -1

            r = self.infile.get_record( i )

            if r == "" or r == "\n": break

            if r['duration'] == 0:
                r['duration'] = 1
          
            if r['packets'] == 0:
                r['packets'] = 1

            pt = [ ord(r['flag']), ord(r['proto']), ord(r['tos']), int(r['packets']), int(r['bytes']),
                    int(r['packets']/r['duration']), int(r['bytes']/r['duration']), int(r['bytes']/r['packets']) ]

            h = Hilbert_to_int( pt ) # flows -> Hilbert
            
            try:
                srcgip = self.i_gip[r['srcip']]
            except:
                # this should never happen.
                print "SRC Error: '"+str(r['srcip'])+"' -> '"+str(self.utils.int2ip( r['srcip'] ))+"'"
                continue

            try:
                dstgip = self.i_gip[r['dstip']]
            except:
                print "DST Error: '"+str(r['dstip'])+"' -> '"+str(self.utils.int2ip( r['dstip'] ))+"'"
                continue

            # replace IP with GROUPIP 

            self.outfile.write( fname + " "+ str(self.flow_counter)+" " )
            self.outfile.write( str(srcgip).strip()+" "+str(r['srcport']).strip()+" "+str(dstgip).strip()+" "+str(r['dstport']).strip()+" ")
            self.outfile.write( str(int(ord(r['proto']))).strip() +" "+str(ord(r['flag'])).strip() +" "+str(ord(r['tos'])).strip() +" ")
            self.outfile.write( str(r['bytes']).strip()+" "+str(r['packets']).strip()+" "+str(r['duration']).strip()+" ")
            self.outfile.write( str( h ) )

            self.outfile.write( "\n")

        os.fsync( self.outfile.fileno() ) 

        # release resources
        self.outfile.close() 
        self.infile.close() 

        self.mylock.release()


################################
######### MAIN TOOL ############
################################
class tool:
    def __init__(self, options):   
        self.option = options
        self.utils              = nf_utils( options ); 

        # Input parameter
        if self.option[ "dataset" ] == None: sys.exit("No Dataset provided") 

        if not os.path.isdir( self.option[ "dataset" ] ): 
            sys.exit("Dataset path error ("+str(self.option['dataset'])+")")

        if not os.path.isdir( self.option[ "outdir" ] ): 
            sys.exit("Outdir error ("+str(self.option['outdir'])+")")

        if not os.path.isfile( self.option[ "groupfile" ] ): 
            sys.exit("groupfile error ("+str(self.option['groupfile'])+")")

        if self.option['k'] == None or self.option['k'] < 0 : 
            sys.exit("K error")

        if self.option['thread'] == None or self.option['thread'] < 1: 
            sys.exit("Max thread error.")

        self.gip                = {}; 
        self.i_gip              = {}; 
        self.getIpGroup()
        self.flow_counter       = -1
        self.gipfiles           = {}
        self.avglist            = {} # avglist[ HILBERTCODE ] = [GIPLEAEDR1, GIPLEAEDR2, ... , GIPLEAEDR1]

        # Multi-thread
        self.maxproc = int( self.option['thread'] )
        self.mylock = threading.BoundedSemaphore( self.maxproc )

    def printIpGroup(self):
        print self.gip

    """
        Search the closest value into a list
    """
    def closestElemInList(self, element, mylist ):
        # perche' non farla parte della classe???
        f = lambda a,l: min(l, key=lambda x:abs(x-a))
        return f( element, mylist )

    """
        Evaluate the groups Hilbert's Average 
    """
    def get_grp_avg(self, elemlist):
        _grpavg = long(0)
        for hvalue in elemlist:
            _grpavg = _grpavg + long( hvalue)

        return float(_grpavg) / float( len( elemlist ) ) 

    """
        Loading Structure 
    """
    def getIpGroup(self):  # loading IpGroup structure
        sys.stdout.write("Loading GIP dict ..."); sys.stdout.flush()
        
        gipfile = open(self.option['groupfile'], 'r')

        while True:
            line = gipfile.readline()
            if line == "" or line == "\n": break
            (_gip,_ip) = line.split(" ")
            ip = _ip.replace("\n","").strip()
            # print _gip + " - '"+str(ip)+"'"
            # if ip == "95.245.22.112":
                # print "TROVATO"

            gip = int( self.utils.ip2int( _gip ) )

            if not self.gip.has_key( gip ):
                self.gip[ gip ] = {'iplist':[], 
                                    'avg':None, 
                                    'helper':None,
                                    'random': None
                                }

            self.gip[gip]['iplist'].append( int( self.utils.ip2int( ip ) ) )

            del line; del gip; del _gip; del ip
        gipfile.close()
        del gipfile

        self.avglist = {}

        """
            Calcolo tutte le medie di Hilbert e l'inverted index
            Se rispetta la P1
                Calcolo un valore Casuale e lo associo al gruppo
            Inverted Index delle medie
        """
        for grpleader in  self.gip.keys():
            # Carico L'Inverted Index per trasformare velocemente un IP in un GROUPIP

            self.gip[grpleader]['avg'] = self.get_grp_avg( self.gip[grpleader]['iplist'] )

            # se il gruppo rispetta P1 lo aggiungo nell'elenco delle medie
            if len( self.gip[grpleader]['iplist'] ) > (self.option['k'] - 1):
                random.seed( grpleader )
                self.gip[grpleader]['random'] = str( random.random() )

                if not self.avglist.has_key( self.gip[grpleader]['avg'] ):
                    self.avglist[ self.gip[grpleader]['avg'] ] = []

                self.avglist[ self.gip[grpleader]['avg'] ].append( grpleader ) 
                
        """     
            Potrebbero esserci anche dei gruppi che ancora non rispettano P1 
            li integro trovando dei gruppi che gli "somigliano"        
        """
        print "Integrate UNSAFE (P1) GROUPS ..."
        p1yetunsafe = 0
        for grpleader in  self.gip.keys():

            if not ( len( self.gip[grpleader]['iplist'] ) > (self.option['k'] - 1) ) : # non rispetta P1
                p1yetunsafe += 1
                # helpercandidate e' la chiave del DICT  
                helpercandidate = self.closestElemInList( self.avglist.keys(), self.gip[grpleader]['avg'] )
                elemento = self.avglist[ helpercandidate ].pop( 0 )

                if len(  self.avglist[ helpercandidate ] ) == 0:
                    del  self.avglist[ helpercandidate ]

                self.avglist[ grpleader ]['helper'] = elemento

                # Valore del GIP per il gruppo che non riflette P1
                random.seed( grpleader + "MYRANDOMSALTHIHIHIHI" + elemento )
                self.gip[grpleader]['random'] = str( random.random() )

                # CAMBIO ANCHE IL GRUPPO HELPER
                # Valore del GIP per il gruppo HELPER del gruppo che non riflette P1
                self.gip[elemento]['random'] = str( random.random() )
        print p1yetunsafe, " unsafe group fixed"
        
        print "Evaluating inverted index ..."
        for grpleader in  self.gip.keys():
            if self.gip[grpleader]['random'] == None: sys.exit("RANDOM NOT FOUND!")

            for intip in self.gip[grpleader]['iplist']:
                self.i_gip[ intip ] = self.gip[grpleader]['random']

        sys.stdout.write("("+str(len(self.gip.keys()))+" gip groups loaded) [DONE]\n")
        sys.stdout.write("Check for unsafe groups")
        sys.stdout.write("[done]\n")

    """
        PRENDO TUTTI I FILE DEL DATASET
    """
    def run(self):

        listing = os.listdir(self.option['dataset'])
        listing.sort()

        i = 0   
        totfile = len( listing )
        totgip  = len( self.gip )

        print "Loaded ", totgip ," groups"

        # For each GIP Group
        gipkeys = self.gip.keys()

        myt = []
        c = 0
        for _infile in listing:    # FOR ALL FILE IN DIR

            self.mylock.acquire()

            c += 1
            tname = "T-"+str(c)
            inputfilepath = self.option['dataset'] + "/" + _infile
            # outfilepath = open( self.option['outdir']+"/"+_infile+".out", 'w')
            outfilepath = self.option['outdir']+"/"+_infile+".out"
            
            # faccio partire il thread
            tfile = nffileProcess( self.mylock, tname, inputfilepath, outfilepath , self.i_gip)
            tfile.start()

            myt.append( tfile )


        # aspetto che tutti i thread abbiano finito
        for a in myt:
            a.join()

        #for f in self.gipfiles: self.gipfiles[f].close()

if __name__ == "__main__":
    # leggi parametri INPUT e capisci cosa fare
    parser = OptionParser()
    parser.add_option("-d", "--dir",        dest="dataset",    default=None, help="original (dataset) input dir")
    parser.add_option("-g", "--grouip",     dest="groupfile",  default=None, help="index file")
    parser.add_option("-k", "--kappa",      dest="k",    type=int,       default=None, help="K")
    parser.add_option("-o", "--out-dir",    dest="outdir",     default=None, help="original (dataset) input dir")
    parser.add_option("-t", "--thread",     dest="thread",     default=None, help="max number of thread")

    (options, args) = parser.parse_args()
    
    print "*************************************\n\
OBFUSCATION 1\n\
"+str(options.__dict__)+"\n\
*************************************\n"

    a = tool(options.__dict__)
    a.run()

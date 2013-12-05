#!/usr/bin/python

""" 
Cosa Fa

Questo script prende in INPUT un file (ORDINATO) contenente gli IP e il 
valore di HILBERT ASSOCIATO e CREA I GRUPPI DI K ELEMENTI IN MANIERA INCREMENTALE.

esempio: python incrementalGroupIP.py -k 10 -o tmp/incremental-gip  -n tmp/ip-hilbert-sorted-prev -f tmp/ip-hilbert-sorted  -g tmp/gip-ip  -c tmp/ipinday

esempio: python incrementalGroupIP.py -k 10 -o tmp/incremental-gip  -n tmp/ip-hilbert-sorted-prev.simple -f tmp/ip-hilbert-sorted.simple  -g tmp/gip-ip.simple  -c tmp/ipinday.simple

"""

import signal
import sys, os, time
from optparse import OptionParser

import bisect # fast search in sorted array

from operator import itemgetter, attrgetter

# alla faccia dell'efficienza :)
from sets import Set

"""
self.gip_db_notp1[ IPasGROUPLEADER ] = { commonIP, }
"""

""" STRUTTURA DATI """

from incremental_2_lib import *

"""
    Classe che contiene il MAIN
"""
class tool:
    def __init__(self, option):
        self.options     = option; 

        self.check()

        self.gip_db                 = {}
        self.new_ips                =  None
        self.gip_db_notp1           = []
        self.final                  = [] # risultati finali ottenuti in fase di costruzione

        self.output = open( self.options['out'], 'w')

    def close(self): self.output.close()

    # Controllo le variabili in INTPUT .. 
    def check(self):
        if self.options['new'] == None or not os.path.exists(self.options['new']):
            sys.exit("New Hilbert file error")

        if self.options['old'] == None or not os.path.exists(self.options['old']):
            sys.exit("Old GIPDB error")

        if self.options['out'] == None: 
            sys.exit("Output file error")

        if self.options['k'] == 0: sys.exit("K must be > 0")


    """ Evaluate the groups Hilbert's Average  """
    def get_grp_avg(self, elemlist):
        _grpavg = long(0)
        for elem in elemlist: 
            _grpavg += long( elem )
        return _grpavg / len( elemlist ) 


    def myhandler(self, sigcode, frame):
        print "[", time.time() ,"] NEWTOT ", self.newtotal, " COUNT", self.counter , " OLD", self.oldtot 

    def outwrite(self, res):
        self.output.write( res )
        
    def get_average( self, commonip ):
        # print "Average of ", commonip
        tmpavglist = []
        # print "New Avg ", len(commonip)
        for ip in commonip:
            hilbert = self.new_ips.get_hilbert( ip ) 
            # print "[AVG] IP-H", ip, "-",hilbert
            tmpavglist.append( hilbert )

        return self.get_grp_avg( tmpavglist )

    """  MAIN FUNCTION  """
    def run(self):
        print self.options
        signal.signal(signal.SIGUSR1, self.myhandler)

        print " ::: Incremental Groupin IP ::: "

        ############  CARICO LE STRUTTURE DATI  ############
        self.counter    = 0 
        self.newtotal   = 0 
        self.oldtot     = 0 

        self.new_ips      = iphibert()
        self.new_ips.load_from_file ( self.options['new'] )
        self.new_ips_keyset = self.new_ips.get_key_set()
        print "Loaded NEW IP done (",self.new_ips.num(),")"

        self.gip_db      = datastruct()
        self.gip_db.load_from_file_asdict ( self.options['old'] )
        print "Loaded GIP_DB done (",self.gip_db.num(),")"

        print "Lunghezza NEW IP ", len( self.new_ips_keyset ) 
        print "Lunghezza GIP DB ", len( self.gip_db.get_elem_set() ) 

        """ ANALISI DEI VECCHI GRUPPI """
        for gip in self.gip_db.t.keys():

            elemofgip = self.gip_db.t[ gip ]

            if elemofgip == None or len( elemofgip ) == 0: 
                sys.exit( "Impossibile my sir!" )

            commonip = Set( elemofgip ) & self.new_ips_keyset  

            if ( len( commonip ) > 0 ) and ( len( commonip ) < self.options['k'] ):
                # Aggiungo il GIP ai GIP che non rispettano P1
                avg = self.get_average( commonip )

                # DEFINIZIONE TUPLA: ( GIP, MEDIA; LISTAIP, IPAGGIUNTI)   
                self.gip_db_notp1.append( (gip, avg, list(commonip), []) )

            # faccio il DUMP dei vecchi GIP per totale che mi porto dietro
            for ip in elemofgip:
                self.outwrite( str(gip) + " " + str(ip) + "\n")

            # cancello gli IP in comune con la nuova release
            for ip in commonip:
                self.new_ips.deleteip( ip ) # cancello gli elementi in comune dai NUOVI IP
                if ip == "117.63.115.167" : print "TROVATO l'IP ", ip 

            self.gip_db.delete( gip )
            del commonip, elemofgip

            """ 
            self.counter += 1

            # prop. P1 mantenuta ?
            elemofgip = self.gip_db.t[ gip ]

            if elemofgip == None or len( elemofgip ) == 0: sys.exit( "Impossibile my sir!" )

            # Calcolo Intersezione tra il Vecchio GIP e tutti i nuovi IP
            commonip = Set( elemofgip ) & self.new_ips_keyset  

            if ( len( commonip ) == 0 ) or ( len( commonip ) >= self.options['k'] ):

                for elem in elemofgip: # metto tutti gli elementi di GIPDB
                    self.outwrite( str(gip) + " " + str(elem) + "\n")

                self.gip_db.delete( gip ) # cancello dalla vecchia GIP [[ a che serve ??? ]]

                # Se c'e' almeno 1 elemento in comune lo cancello anche dai nuovi
                if len( commonip ) >= self.options['k']:
                    for n_ip in commonip: 
                        self.new_ips.deleteip( n_ip ) # cancello dai nuovi IP quelli comuni

                del elemofgip, commonip
                continue

            # Arrivati qui il gruppo ha un numero di elementi in comune X t.c. 0 <X<k 
            # quindi il gruppo non mantiene P1

            # calcolo la lista degli elementi comuni del gruppo
            avg = self.get_average( commonip )

            # DEFINIZIONE TUPLA: ( GIP, MEDIA; LISTAIP, IPAGGIUNTI)   
            self.gip_db_notp1.append( (gip, avg, list(commonip), []) )

            # cancello gli IP che sono in COMUNE (e quindi anche in R1)
            for ip in commonip:
                print "Cancello", ip
                self.new_ips.deleteip( ip ) 
                if ip == "117.63.115.167" : print "TROVATO l'IP ", ip 

            uncommon = Set( elemofgip ) - Set ( list(commonip) ) 
            for elem in list( uncommon ): # metto tutti gli elementi
                self.outwrite( str(gip) + " " + str(elem) + "\n")

            self.gip_db.delete( gip )
            del commonip, elemofgip
            """ 

        """
        FINE ANALISI DEI VECCHI GRUPPI
        """

        # tutti i vecchi gruppi o sono NOTP1 o rispettano P1
        print "Dei vecchi gruppi, ne son rimasti ", self.gip_db.num()

        # non avrebbe senso perche' ho fatto un ciclo fir su GIPDB
        if self.gip_db.num() > 0:
            sys.exit( "ERRORE, terminati self.gip_db" ) 
        del self.gip_db 

        print "Ci sono ", len( self.gip_db_notp1 ), " gruppi che non rispettano P1"

        # ORDINO L'INSIEME DI TUPLE PER MEDIA DI AVERAGE
        sorted( self.gip_db_notp1, key=itemgetter(1) ) 

        # for (gip, avg, commonip, extendedip) in self.gip_db_notp1:
        while len( self.gip_db_notp1 ) > 0:
            (gip, avg, commonip, extendedip) = self.gip_db_notp1.pop()

            # print "For: ", (gip, avg, commonip, extendedip)  

            whileloop = True

            while whileloop:

                # Cerco ip con H piu' vicino a self.gip_db_notp1[gip][avg] e lo prendo da self.new_ips
                # (ip, hilbert) = self.new_ips.search( t[ avgindex ], 1 ) # TODO: cambiare con bisect
                # print "LISTA -> ", self.new_ips.t
                # print "TYPE", type(t[ avgindex ] )
                index = self.new_ips.search( avg ) # TODO: cambiare con bisect

                # if index == 0: 
                # index = 1 
                # else:
                if index > 0 :
					index = index - 1

                if index == None: 
                    whileloop = False; 
                    # print "Index = None"
                    break # ho finito gli elementi

                try:
                    (hilbert, ip) = self.new_ips.t[ index ]
                except:
                    #print "Lunghezza lista rimasta:", len( self.new_ips.t )
                    #print "Indice Richiesto:", index
                    #print "Uscita Forzata!"
                    sys.exit()

                # print "[H:",avg," -> IND ",index,"]", (ip, hilbert)

                # ho finito gli elementi ?
                if ( ip == None or hilbert == None ): 
                    whileloop = False 
                    #print "Uscito qui"
                    break 

                # print "IP, HILBERT ", ip, hilbert , " TIPI", type(ip), type(hilbert )
                # self.new_ips.delete( ip, hilbert )

                self.new_ips.deleteip( ip )

                extendedip.extend ( [ ip ] ) # aggiungo l'IP alla lista degli IP trovati

                if ( len( extendedip ) + len( commonip ) ) >= self.options['k']:
                    """
                    gli elementi (IP) nuovi li cancello giusto prima
                    gli elementi (IP) in comune li cancello nella prima fase 
                    """
                    l = list( Set( extendedip ) ) 
                    for elem in l:
                        self.outwrite( str( gip ) + " " + str( elem ) + "\n")

                    l = list( Set( commonip ) ) 
                    for elem in l:
                        self.outwrite( str( gip ) + " " + str( elem ) + "\n")
                    
                    whileloop = False 

            # print "USCITO per T", (gip, avg, commonip, extendedip)
            # self.gip_db_notp1.remove( (gip, avg, commonip, extendedip) )
            
        if len( self.gip_db_notp1 ) > 0 :
            print str( len( self.gip_db_notp1 ) )+" GIP with no P1 ; "+str( self.new_ips.num() )+" new ips yet!"
        
            sys.exit("EXIT")

        del self.gip_db_notp1

	print "Inizio con nuovi IP"

        kgroup = []
        oldleader = None
        # for (ip,hilbert) in self.new_ips.get_data():
        for (hilbert,ip) in self.new_ips.get_data():

            kgroup.append( ip ) 

            if len( kgroup ) >= self.options['k']:
                oldleader = kgroup[0]
                for ipk in kgroup:
                    # self.output.write( str( oldleader ) + " " + str( ip ) + "\n")
                    self.outwrite( str( oldleader ) + " " + str( ipk ) + "\n" )
                kgroup = []

        # eventuali elementi residui!
        for ip in kgroup:
            # self.output.write( str( oldleader ) + " " + str( ip ) + "\n")
            self.outwrite( str( oldleader ) + " " + str( ip ) + "\n" )

        print "Flushed new IPS"
        print str( self.new_ips.num() )+" new ips yet!"

        self.output.flush()
        self.output.close()

        """ CODICE DI VERIFICA """ 
        f = open( self.options['out'] ,'r')
        t = []
        g = []
        while True:
            line = f.readline()
            if line == None or line == "": break
            _ip = line.split(" ")
            t.append( _ip[1] )
            g.append( _ip[0] )
        f.close
        print "IPDIVERSI:" , len(t), " - ", len( Set( t ) )
        print "GIP:" , len(g), " - ", len( Set( g ) )
        sys.exit("FINE")

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--new",   dest="new",  default=None, help="New IP hilbert file")
    parser.add_option("-g", "--old",   dest="old",  default=None, help="old GIP DB file")

    parser.add_option("-o", "--out",    dest="out",      default=None, help="output file ")
    parser.add_option("-k", "--kappa", default=0,   dest="k", type=int, help="K param")
    print "\
*************************************\n\
INCREMENTAL GROUP DEFINITION\n\
*************************************\n"
    (options, args) = parser.parse_args()

    a = tool(options.__dict__)
    a.run()

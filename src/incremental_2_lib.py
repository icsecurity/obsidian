from sets import Set
import bisect
import sys

#class datastruct:
#    def __init__(self):
#        self.t = []

""" FINE STRUTTURA DATI IP - HILBERT  """
class iphibert:
    def __init__(self):
        self.t      = []
        self.inv_t  = {}

    def get_data(self):
        return self.t

    def insert(self, ip, hilbert):
        # bisect.insort( self.t, (key,elem) )
        self.t.append( ( long( hilbert ) ,ip) )  # i valori arrivano ordinati per Hilbert
        if self.inv_t.has_key( ip ):
            print "Errore: un ip non puo' avere piu' HILBERT"
            sys.exit( 0 )
        self.inv_t[ ip ] = long( hilbert )

        #self.ips = self.ips & Set( [elem] )
        # sys.stdout.write(".")

    def num(self): return len( self.t )

    def get_hilbert(self, ip):
        if not self.inv_t.has_key( ip ): 
            print "Hilbert not found per IP",ip
            return None
        return self.inv_t[ ip ] 

    def search(self, key, elem=None):
        if len(  self.t ) == 0 : 
            return None

        if elem == None:
            index = bisect.bisect( self.t, (key,) )
        else:
            index = bisect.bisect( self.t, (key,elem) )

        return index

    def get_key_set(self):
        return self.get_elements(1)

    def get_elem_set(self):
        return self.get_elements(0) 
 
    def get_elements(self, elemindex):
        res = []
        [ res.extend( [ y[ elemindex ] ] ) for y in self.t ]
        return Set( res ) 
        

    def deleteip(self, ip):
        if self.inv_t.has_key( ip ):
            self.t.remove( ( self.inv_t[ ip ] ,ip) ) 
            del self.inv_t[ ip ]
        else:
            # print self.inv_t
            print "IP",ip,"non trovato"

    def deletehilbert(self, hilbert):
        ind = self.search( hilbert )        
        ( hilbert, ip ) = self.t [ ind - 1 ]
        self.t.remove( ( hilbert, ip ) )
        del self.inv_t[ ip ] 

    def load_from_file(self, fname):
        tempf   = open( fname , 'r' )
        content = tempf.read() # readallfile
        tempf.close(); del tempf;

        for line in content.split("\n"):
            if line == "":  break
            (_ip, _hilbert) = line.split() ; del line

            ip = str( _ip ).strip() ; del _ip
            hilbert = str( _hilbert ).strip() ; del _hilbert

            # self.insert( key, elem)
            self.insert( ip, hilbert)

""" FINE STRUTTURA DATI IP - HILBERT  """

""" STRUTTURA DATI DICT  """
class datastruct:
    def __init__(self):
        self.t = {}

    def num(self):
        return len( self.t.keys() ) 

    def insert(self, key, elem):
        if not self.t.has_key( key ):
            self.t[ key ] = [] 
        self.t[ key ].append( elem )


    def load_from_file_asdict(self, fname, excludelist=None):
        self.load_from_file(fname) 

    def load_from_file(self, fname):
        tempf   = open( fname , 'r' )
        content = tempf.read() # readallfile
        tempf.close(); del tempf;

        for line in content.split("\n"):
            if line == "":  break
            (_key, _elem) = line.split() ; del line

            key = str( _key ).strip() ; del _key
            elem = str( _elem ).strip() ; del _elem 

            self.insert( key, elem)

    def delete(self, key, elem=None):

        if not self.t.has_key( key ): return None

        if elem == None:
            del self.t[ key ]
            return True

        if not ( elem in self.t[ key ] ): 
            return None

        self.t[ key ].remove ( elem ) 

    def get_key_set(self):
        return Set( self.t.keys() )

    def get_elem_set(self):
        res = []
        [res.extend( self.t[y] ) for y in self.t.keys()]
        return Set( res ) 

    def loadfromkeyset(self, inkeyset):
        for key in inkeyset:
            self.insert(key, None)

""" FINE STRUTTURA DATI DICT  """



class datastruct_old:
    def __init__(self):

        self.keyset     = Set()
        self.elemset    = Set()
        self.direct     = None
        self.t          = [] 
        self.struct     = []


    # ORDINA
    def sortbykey(self):
        sorted(self.t,  key=itemgetter(0))

    def sortbyelem(self):
        sorted(self.t,  key=itemgetter(1))

    """ CARICAMENTO DA FILE """
    def load_from_file_asdict(self, fname, excludelist=None):
        self.direct = {}
        tempf   = open( fname , 'r' )
        content = tempf.read() # readallfile
        tempf.close(); del tempf;

        for line in content.split("\n"):
            if line == "":  break

            (_key, _elem) = line.split() ; del line

            key = str( _key ).strip() ; del _key
            elem = str( _elem ).strip() ; del _elem 

            if not excludelist == None:
                if key in excludelist: 
                    continue

            if not self.direct.has_key( key ):
                self.direct[ key ] = []
            self.direct[ key ].append( elem )

            del key, elem;
        del content

    # loading data from file
    def load_from_file(self, fname):

        self.struct.append( 'tuple' )

        tempf   = open( fname , 'r' )
        content = tempf.read() # readallfile
        tempf.close(); del tempf;

        for line in content.split("\n"):
            if line == "":  break

            (_key, _elem) = line.split() ; del line

            key = str( _key ).strip() ; del _key
            elem = str( _elem ).strip() ; del _elem 

            try:
                self.t.append( (key, long( elem ) ) )
            except:
                self.t.append( (key, elem ) )

    def get_data(self):
        return self.t

    """ CARICAMENTO DEI DATI """
    def load_keyset(self):
        if not self.direct == None:
            self.keyset = Set( self.direct.keys() ) 
            return 

        self.keyset = Set( [ x[0] for x in self.t ] ) 

    #### IMPOSTA LA STRUTTURA DAL SET E CARICA IL KEY-LIST ORDINANDOLO
    def set_keyset(self, keyset):
        self.keyset = keyset
        self.t = [ (x,"") for x in self.keyset ]

    #### RESTITUISCE GLI ELEMENTI DI UNA CHIAVE
    def elemof(self, key):
        if not self.direct == None:
            return self.direct[ key ]

        (k,v) = self.search(key, index = 0)

        if k == None: 
            return None

        return v

    def get_keyset(self):
        if not self.direct == None:
            return Set( self.direct.keys() ) 
        return Set( [ x[0] for x in self.t ] ) 

    def get_keys(self):
        if not self.direct == None:
            return self.direct.keys()
        return [ x[0] for x in self.t ]

    def delete(self, key, elem=None):
        # Se utilizzo come struttura dati il DICT
        if not self.direct == None:
            del self.direct[ key ]
            return 

        # Se fornisco anche l'elemento, non devo fare la ricerca
        k = key
        v = elem

        if elem == None:
            # (k,v) = self.search ( key, 0)
            (kt,vt) = bisect.bisect( self.t, (k,) )
            if kt == k:
                print "ERRR ::: Key non trovata"
                return None
            if k == None: 
                print "ERRR ::: Non trovato: vuoto? "
                return None

        try:
            self.t.remove( (k, v) )
        except:
            print "Error deleting (K,V)=(",key,",",elem,") => (",k,",",v,") non riuscita  perche' non trovato !"
            return None
            
        return True

    def num(self):
        if not self.direct == None:
            return len( self.direct.keys() )

        return len( self.t )

    """ RICERCA """
 
    def searchbyelem(self, value):
        return self.search(value, index = 1)

    def searchbykey(self, value):
        return self.search(value, index = 0)

    def search(self, elem, index = 0):
        lo=0
        hi = len( self.t ) - 1

        last = None

        while lo < hi:
            mid = (lo+hi) / 2 # prendo valore medio 
            last = self.t[ mid ]
            # last = (midval[0], midval[1])

            # Analizzo il valore dell'elemento
            if last[ index ] < elem: 
                lo = mid + 1

            elif last[ index ] > elem: 
                hi = mid

            else: 
                return last

        return last 


#!/usr/bin/python
"""
This class provide a useful interface to meta-index of statdb binary file.
"""
import os, sys, struct 
# from nf_map_file import *
from nfutils import *

class simpleindex:
    def __init__(self, index_file_name):
        self.index_format       = "IIIII"
        self.index_format_size  = struct.calcsize( self.index_format )
        self.indexfilename      = index_file_name
        self.nf_index           = []
        self.init_index()   
        self.distinct_ip        = 0  
        self.f  = None

    def newindex(self):
       self.f = open( self.indexfilename , 'wb')
        
    def debug(self, msg):
        print "[nf_statdb_index] ", msg            

    def stat(self):
        return "[STAT] nf_index ->"+str(sys.getsizeof(self.nf_index))+" ["+str(self.distinct_ip)+" distinct IP]"
        
    # Alloca "static" structure 65.536 dictionaries
    def init_index(self):
        self.debug("Init index...")
        self.nf_index = [ [ {} for y in range (256)] for x in range(256)]

    def update_index(self, ip, seek):
        # ip = [int(sep[0]), int(sep[1]), int(sep[2]), int(sep[3])]
        # if   self.nf_index[ int(ip[3]) ][ int(ip[2]) ].has_key( int(ip[1]) ):
        # corretto in data 24 luglio
        if  not self.nf_index[ int(ip[3]) ][ int(ip[2]) ].has_key( int(ip[1]) ):
            self.nf_index[ int(ip[3]) ][ int(ip[2]) ][ int(ip[1]) ] = {}

        if  not self.nf_index[ int(ip[3]) ][ int(ip[2]) ][ int(ip[1]) ].has_key( int(ip[0]) ):
            self.distinct_ip += 1
        
        self.nf_index[ int(ip[3]) ][ int(ip[2]) ][ int(ip[1]) ][ int(ip[0]) ] = seek
        # print "INDEX UPDATE:", int(ip[3]), int(ip[2]) , int(ip[1]), int(ip[0]), " -> ", seek
        del ip, seek

    """
        Load from FILE an index structure 
    """
    def load_index(self):
        c = 0

        if os.path.getsize( self.indexfilename ) == 0: sys.exit("Empy index file " + self.indexfilename)

        if self.f == None:
            self.f = open(self.indexfilename, "r+b")

        self.debug("Loading index file: " + self.indexfilename )
        # raw_input()
        # f = open( self.indexfilename , 'rb')
        while True:
            ret = self.f.read( self.index_format_size )
            if len(ret) == 0:
                break

            qo,to,j,i,seek = struct.unpack( self.index_format, ret )

            # print "Letti " ,qo,to,j,i, " SEEK ", seek
            # raw_input()

            if not self.nf_index[i][j].has_key(to):
                self.nf_index[i][j][to] = {}
            self.nf_index[i][j][to][qo] = seek
            if c == 1:
                print i ,".", j,"." , to,".", qo," -> s",self.nf_index[i][j][to][qo]
            c += 1
            del ret, i, j, to, qo
        # raw_input()
            
        print "Index size: ", c
        
    # This function print index. Results can be selected using search parameter as arbitrary lenght substring of IP string
    def print_index(self, search=None):  
        for i in range(256):
            for j in range(256):
                for t in self.nf_index[i][j]:
                    for q in self.nf_index[i][j][t]:
                        if not search == None and search.count( str(self.nf_index[i][j][t]) ) == 0:
                            continue
                        self.debug("IP "+str(i)+"."+str(j)+"."+str(t)+"."+str(q)+": "+str(self.nf_index[i][j][t][q]))

        del i, j, t, q

    def write_index_entry(self, (q,t,j,i) , seek):
        self.f.write( struct.pack( self.index_format , int(q),int(t),int(j),int(i), int( seek ) ) ) 

    def write_index(self):
        c = 1 
        for i in range(256):
            for j in range(256):
                for to in self.nf_index[i][j].keys():
                    for qo in self.nf_index[i][j][to]:
                        self.f.write( struct.pack( self.index_format , int(qo),int(to),int(j),int(i), int( self.nf_index[i][j][to][qo] ) ) )
                        #if c == 1:
                            # print i ,".", j,"." , to,".", qo," -> s",self.nf_index[i][j][to][qo]
                            # continue
                        c += 1
                        del qo
                    del to; 
        del i; del j; 
    
        self.f.flush()
        os.fsync( self.f.fileno() ) 
        size = os.path.getsize( self.indexfilename )
        self.debug("Written " + str(size) + " bytes [ "+str( int(size/self.index_format_size))+" record of "+str(self.index_format_size)+" bytes]")

    def close(self):
        self.f.close()

    # According to indexing policies, IP value is reversed
    def record_seek(self, ip): 
        # print "RECORD SEEK ", ip , "CERCO IN ", ip[3], " -> ",ip[2]
        if not self.nf_index[ip[3]][ip[2]].has_key( ip[1] ):
            self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ] = {}

        if not self.nf_index[ip[3]][ip[2]][ ip[1] ].has_key( ip[0] ):
            self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ][ ip[0] ] = 0
            return None
        return self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ][ ip[0] ]

        """
        if self.nf_index[ip[3]][ip[2]].has_key( ip[1] ):
            try:
                return self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ][ ip[0] ]
            except:
                return None
        else:
            # creo l'elemento dell'indice e lo imposto a zero..
            self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ] = {}
            self.nf_index[ ip[3] ][ ip[2] ][ ip[1] ][ ip[0] ] = 0
            # print "TOUCH: ", ip[3],"->",ip[2],"->",ip[1],"->",ip[0]
            return None
        """

    def has_node(self, index, elem):
        if len(index) == 2:
            return self.nf_index[ index[0] ][ index[1] ].has_key( elem )

        if len(index) == 3:
            return self.nf_index[ index[0] ][ index[1] ][ index[2] ].has_key( elem )

        return None

    # riceve un'array in senso inverso
    def get_ips_by_index(self, index):
        if len(index) == 2:
            try:
                return self.nf_index[ index[0] ][ index[1] ].keys()
            except:         
                return {}
        if len(index) == 3:
            try:
                return self.nf_index[ index[0] ][ index[1] ][ index[2] ].keys()
            except:         
                return {}
        if len(index) == 4:
            try:
                return self.nf_index[ index[0] ][ index[1] ][ index[2] ][ index[3] ]
            except:         
                return {}

    # riceve una stringa IP dritto!
    def get_by_index(self, ip):
        (i,j,t,q) = ip.split(".")
        # print "PRENDO IL SEEK DI ", ip , " : ", int(q),"->",int(t),"->",int(j),"->",int(i)
        return self.nf_index[ int(q) ][ int(t) ][ int(j) ][ int(i) ]

    def get_seek_by_index(self, index):
        if not self.nf_index[ int(index[0]) ][ int(index[1]) ].has_key(int(index[2])):
            return None
        if self.nf_index[ int(index[0]) ][ int(index[1]) ][ int(index[2]) ].has_key(int(index[3])):
            return self.nf_index[ int(index[0]) ][ int(index[1]) ][ int(index[2]) ][ int(index[3]) ]


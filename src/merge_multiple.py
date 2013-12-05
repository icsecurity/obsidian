#!/usr/bin/python

import os
import sys
import struct 
import threading
from sets import *

from optparse import OptionParser
# from nf_merger import *
from dbindex import *

class tool:
    def __init__(self, options):
        self.option = options
        print self.option
        if self.option['outputfile'] == None: sys.exit("Ourfile error")
        if self.option['statdbfiles'] == None: sys.exit("Input error")
                               
        self.structformat   = "IILLffILffffffffffffff"
        self.structsize     = struct.calcsize( self.structformat )

        # self.merger = nf_merger()

        self.indexformat   = "IIIII"
        self.indexstructsize    = struct.calcsize( self.indexformat )

        self.inputs = {}
        # self.indexes    = []
        # self.statfile   = []

        self.resindex = simpleindex( str( self.option['outputfile'] ) + ".idx" )
        self.resindex.newindex()

        self.out = open( self.option['outputfile'] , 'w+b')

        # Controllo l'esistenza di tutti file che devo "mergiare"
        for statfile in self.option['statdbfiles']:
            if not os.path.exists( statfile ):
                sys.exit("Err: File "+str(statfile)+" does not exists!") 

            a = simpleindex( str(statfile)+".idx")
            a.load_index()

            self.inputs[ statfile ] = {'openfile':open( statfile, "rb") , 'index': a }

            # self.indexes.append( a )
            # self.statfile.append( open( statfile, "r")  )

    """ Close connections and free resources """
    def close(self):
        for stat in self.inputs.keys():
            self.inputs[ stat ]['index'].close()
            self.inputs[ stat ]['openfile'].close()

        print "Flush output file"
        self.out.flush()
        os.fsync( self.out.fileno() )
        self.out.close()

        # print "Flush Index file" -> non serve perche' alla fine lo scrivo piano piano
        # self.resindex.write_index()

    def get_record(self, statfile,  i):
        pass

    def init_rec(self):
        ret = {}
        ret["counter"] = 0
        ret["ba"]      = 0
        ret["ba2"]     = 0
        ret["pa"]      = 0
        ret["pa2"]     = 0
        ret["ppsa"]    = 0
        ret["ppsa2"]   = 0
        ret["bpsa"]    = 0
        ret["bpsa2"]   = 0
        ret["bppa"]    = 0
        ret["bppa2"]   = 0

        ret["bm"]    =  0
        ret["pm"]    =  0
        ret["bpsm"]  =  0
        ret["ppsm"]  =  0
        ret["bppm"]  =  0
        ret["bd"]    =  0
        ret["pd"]    =  0
        ret["bpsd"]  =  0
        ret["ppsd"]  =  0
        ret["bppd"]  =  0
        return ret

    def run(self):

        for i in range(256):
            for j in range(256):

                # Trovo tutti i T
                all_t = Set( [] )

                for stat in self.inputs.keys():
                    tindex = self.inputs[ stat ]['index']
                    # print "I",i,"J",j,"->TROVATI", tindex.get_ips_by_index( [i,j] )
                    all_t |= Set( tindex.get_ips_by_index( [i,j] )  )
                # print "Per ",i,".",j," trovati ", len (all_t) , " elementi."

                # if len( all_t ) == 0: 
                    # print "Non ho trovato nulla!"

                for t in all_t:
    
                    # Trovo tutti i Q
                    all_q = Set( [] )
                    for stat in self.inputs.keys():
                        tindex = self.inputs[ stat ]['index']
                        all_q |= Set( tindex.get_ips_by_index( [i,j,t] ) )
                    # print "Per ",i,".",j,".",t," trovati ", len (all_q) , " elementi."

                    for q in all_q:

                        temp = self.init_rec()

                        # Pre ogni indice, trovo l'elemento [ se esiste ]
                        for stat in self.inputs.keys():
                            tindex = self.inputs[ stat ]['index']
                            
                            if not tindex.has_node( [i,j], t ): continue
                            if not tindex.has_node( [i,j,t], q ): continue

                            ip = str(q)+"."+ str(t)+"."+ str(j) +"."+str(i)
                            seek = tindex.get_by_index( ip ) # Prendo il seek nel file

                            self.inputs[ stat ]['openfile'].seek( seek )
                            ret = self.inputs[ stat ]['openfile'].read( self.structsize )
                            data = self.bin2data( ret )
                            # print data
                            # raw_input()
                            temp["counter"] += data["counter"] 
                            temp["ba"]      += data["ba"] 
                            temp["ba2"]     += data["ba2"] 
                            temp["pa"]      += data["pa"] 
                            temp["pa2"]     += data["pa2"] 
                            temp["ppsa"]    += data["ppsa"] 
                            temp["ppsa2"]   += data["ppsa2"] 
                            temp["bpsa"]    += data["bpsa"] 
                            temp["bpsa2"]   += data["bpsa2"] 
                            temp["bppa"]    += data["bppa"] 
                            temp["bppa2"]   += data["bppa2"] 

                        temp['bm']      = float(temp['ba']) / float(temp['counter'])
                        temp['pm']      = float(temp['pa']) / float(temp['counter'])
                        temp['bpsm']    = float(temp['bpsa']) / float(temp['counter'])
                        temp['ppsm']    = float(temp['ppsa']) / float(temp['counter'])
                        temp['bppm']    = float(temp['bppa']) / float(temp['counter'])

                        unosun = 1.0/float(temp['counter'])

                        temp['bd']   = ( float(temp['counter'])*float(temp['bm'])*float(temp['bm']) ) + \
                            ( float(temp['ba2']) )-(2.0*float(temp['bm'])*float(temp['ba']))

                        temp['pd']   = ( float(temp['counter'])*float(temp['pm'])*float(temp['pm']) ) + \
                            ( float(temp['pa2']) )-(2.0*float(temp['pm'])*float(temp['pa']))

                        temp['bpsd'] = ( float(temp['counter'])*float(temp['bpsm'])*float(temp['bpsm']) ) + \
                            ( float(temp['bpsa2']) )-(2.0*float(temp['bpsm'])*float(temp['bpsa']))

                        temp['ppsd'] = ( float(temp['counter'])*float(temp['ppsm'])*float(temp['ppsm']) ) + \
                            ( float(temp['ppsa2']) )-(2.0*float(temp['ppsm'])*float(temp['ppsa']))

                        temp['bppd'] = ( float(temp['counter'])*float(temp['bppm'])*float(temp['bppm']) ) + \
                            ( float(temp['bppa2']) )-(2.0*float(temp['bppm'])*float(temp['bppa']))
                        # Aggiungere self.add_record()

                        bintemp = self.data2bin( temp ) 
                        recseek = self.out.tell()
                        
                        self.out.write( bintemp )
                        
                        self.resindex.write_index_entry( (int( q ), int( t ), int( j ), int( i )) , recseek)
                        del temp

        self.close()

    def data2bin( self, c ):

        # for k in c.keys(): 
            #print "K", k , "(", type( c[k]) ,")"

        # print "BA2 ", c['ba2'], " -> ", type( c['ba2'] )

        cba2h = long(c['ba2']) >> 64  
        cba2l = long(c['ba2']) & 0xFFFFFFFFFFFFFFFF 
        # IILLffILffffffffffffff
        return struct.pack(self.structformat, int(c['counter']), c['ba'] , cba2h, cba2l ,float(c['bm']),float(c['bd']), 
                                                      c['pa'],c['pa2'],float(c['pm']),float(c['pd']),
                                                      float(c['ppsa']),float(c['ppsa2']),float(c['ppsm']),float(c['ppsd']),
                                                      float(c['bpsa']), float(c['bpsa2']),float(c['bpsm']),float(c['bpsd']),
                                                      float(c['bppa']), float(c['bppa2']),float(c['bppm']),float(c['bppd']))

    def bin2data(self, ret):
        # IILLffILffffffffffffff
        if len ( ret ) < 104:
            print "Lunghezza ", len(ret)
            # sys.exit( "ERRORE ")
        result = struct.unpack(self.structformat, ret)

        # print "BIN2DATA, letto:", result

        ret =  { "counter": result[0], 
                    "ba":result[1], "ba2": result[3] | (result[2] << 64) , "bm":result[4], "bd":result[5], 
                    "pa":result[6], "pa2":result[7], "pm":result[8], "pd":result[9],
                    "ppsa":result[10], "ppsa2":result[11], "ppsm":result[12], "ppsd":result[13],
                    "bpsa":result[14], "bpsa2":result[15], "bpsm":result[16], "bpsd":result[17],
                    "bppa":result[18], "bppa2":result[19], "bppm":result[20], "bppd":result[21] 
                }
        return ret

""" MAIN """
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--stat-db", dest="statdbfiles", action="append", default=None, help="input dir")
    parser.add_option("-o", "--output",  dest="outputfile", default=None, help="output dir")

    (options, args) = parser.parse_args()

    print "\
*************************************\n\
    FUSION\n\
*************************************\n"
    a = tool( options.__dict__ )
    a.run()


#!/usr/bin/python

import sys, os
import struct


class nfcommon:
    def __init__(self):
        self.structformat = "IILLffILffffffffffffff"

        self.indexstructformat = "IIIII"



    def getdatasize(self):
        return struct.calcsize( self.structformat )

    def getindexsize(self):
        return struct.calcsize( self.indexstructformat )


    """ MODEL FOR STATISTICAL DATABASE """
    def data2bin(self, c ):

        cba2h = c['ba2'] >> 64
        cba2l = c['ba2'] & 0xFFFFFFFFFFFFFFFF
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


import os, sys, socket, struct

class nf_utils:
    def __init__(self, opt=None):
        self.option = opt

    def ip2int(self, ip):
        try:
            return int(socket.htonl( struct.unpack('L',socket.inet_aton(ip))[0] ) )
        except:
            return socket.htonl( struct.unpack('I',socket.inet_aton(ip))[0] )

    def int2ip(self, ip):
        try:
            return socket.inet_ntoa( struct.pack('L', socket.ntohl( ip ) ) )
        except:
            return socket.inet_ntoa( struct.pack('I', int(socket.ntohl( ip ))) )

# non usata
class nf_debug:
    # TODO: implementare il fatto che stampi il nome della classe chiamante
    def __init__(self, msg, level="warning", line=False):
        self.accepted_level = ["error", "warning", "all"]
        self.debug_level    = level
        self.line           = "\n"
        if line == True:
            self.line       = ""
        if not self.debug_level in self.accepted_level:
            self.debug_level    = "U-", level

        self.nf_print()

    def nf_print(self):
        sys.out.write("["+self.debug_level+"] " + msg + self.line)



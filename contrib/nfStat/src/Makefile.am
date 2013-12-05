util = util.c util.h nf_common.c nf_common.h
filelzo = minilzo.c minilzo.h lzoconf.h lzodefs.h nffile.c nffile.h nfx.c nfx.h
nflist = flist.c flist.h 
stats = stats_common.c stats_common.h kullback_entropy.c kullback_entropy.h basic_stats.c basic_stats.h renyi.c renyi.h histo_stats.c histo_stats.h\
		nfsort.c nfsort.h

bin_PROGRAMS = nfStat
nfStat_CFLAGS = -O3 -Wall -lm -fopenmp -msse -g
nfStat_SOURCES = nfStat.c nfStat.h $(util) $(filelzo) $(nflist) $(stats)
CFLAGS =

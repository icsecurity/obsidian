#include "config.h"

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdarg.h>
#include <errno.h>
#include <time.h>
#include <string.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <limits.h>
#include <sys/param.h>
#include <fcntl.h>
#include <sys/socket.h> /* for socket(), connect(), send(), and recv() */
#include <arpa/inet.h>  /* for sockaddr_in and inet_addr() */
#include <sys/ipc.h>
#include <sys/sem.h>

#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif

#include "nfStat.h"
#include "nffile.h"
#include "nfx.h"
#include "util.h"
#include "flist.h"
#include "nf_common.h"
#include "stats_common.h"
#include "kullback_entropy.h"
#include "basic_stats.h"
#include "renyi.h"
#include "histo_stats.h"
#include "nfsort.h"

// module limited globals
extension_map_list_t extension_map_list;
extern headerlist_t header_list;
extern float alpha;
extern double threshold;
uint16_t nf_stat = 0;

//array of list
flowslist_t flow_records[FILESBLK];
common_record_t in_buff[BUFFSIZE];
uint32_t blksize = DEFAULT_BLK_SIZE;

//void (*process_block)(flowslist_t *flow_records, uint32_t ei,uint32_t blksize,int *outfd);

/* Function Prototypes */
static void usage(char *name);

void print_record(void *record, char *s);

/* Functions */
#include "nffile_inline.c"

//K:B:Y:H:a:O:
static void usage(char *name) {
	printf("usage %s [options] \n"
		"-h\t\tthis text you see right here\n"
		"-r\t\tread input from file\n"
		"-s\tstart timestamp (YYYY-MM-DD HH:MM:SS)\n"
		"-e\tend timestamp (YYYY-MM-DD HH:MM:SS)\n"
	      "-d\tduration in block from start time\n"
		"-b\tdimension of the block (seconds)\n"
            "-M <expr>\tRead input from multiple directories.\n"
            "-R <expr>\tRead input from sequence of files.\n"
	      "======= STATISTICS ========\n"
	      "-K <expr>\tKullback Leibler on [NONE|SRCIP|DSTIP|SRCIP_SRCPORT|DSTIP_DSTPORT] if expr [0|1|2|3|4]\n"
	      "-B <expr>\tBasic Stats (flows,bytes,packets) on [NONE|SRCIP|DSTIP|SRCIP_SRCPORT|DSTIP_DSTPORT] if expr [0|1|2|3|4]\n"
	      "-Y <expr>\tRenyi Stat on [NONE|SRCIP|DSTIP|SRCIP_SRCPORT|DSTIP_DSTPORT] if expr [0|1|2|3|4]\n"
	      "-H <expr>\tHistogram stats on [NONE|SRCIP|DSTIP|SRCIP_SRCPORT|DSTIP_DSTPORT] if expr [0|1|2|3|4]\n"
	      "-S sort netflow data \n"
	      "-a <expr>\talpha value of Renyi stat\n"
	      "-O\toutput file name\n", name);
} /* usage */


uint8_t tcpflags[] = {1,2,4,8,16,32};

void print_record(void *record, char *s) {

	char as[40], ds[40], datestr1[64], datestr2[64],proto[16],
		flags[6] = {'.','.','.','.','.','.'};
	time_t when;
	struct tm *ts;
	master_record_t *r = (master_record_t *) record;
	float duration ;

#ifdef IPV6
	if ((r->flags & FLAG_IPV6_ADDR) != 0) { // IPv6
		r->v6.srcaddr[0] = htonll(r->v6.srcaddr[0]);
		r->v6.srcaddr[1] = htonll(r->v6.srcaddr[1]);
		r->v6.dstaddr[0] = htonll(r->v6.dstaddr[0]);
		r->v6.dstaddr[1] = htonll(r->v6.dstaddr[1]);
		inet_ntop(AF_INET6, r->v6.srcaddr, as, sizeof(as));
		inet_ntop(AF_INET6, r->v6.dstaddr, ds, sizeof(ds));
	} else
#endif
	{ // IPv4*/
		r->v4.srcaddr = htonl(r->v4.srcaddr);
		r->v4.dstaddr = htonl(r->v4.dstaddr);
		inet_ntop(AF_INET, &r->v4.srcaddr, as, sizeof(as));
		inet_ntop(AF_INET, &r->v4.dstaddr, ds, sizeof(ds));
	}
	as[40 - 1] = 0;
	ds[40 - 1] = 0;

	when = r->first;
	ts = localtime(&when);
	strftime(datestr1, 63, "%Y-%m-%d %H:%M:%S", ts);

	when = r->last;
	ts = localtime(&when);
	strftime(datestr2, 63, "%Y-%m-%d %H:%M:%S", ts);
	duration = r->last - r->first;

    /*
     * 	000001 FIN.
     * 	000010 SYN
	 *	000100 RESET
	 *	001000 PUSH
	 *	010000 ACK
	 *	100000 URGENT
     */

	 if(TestFlag(r->tcp_flags,tcpflags[0]) == tcpflags[0]) flags[5] = 'F';
	 if(TestFlag(r->tcp_flags,tcpflags[1]) == tcpflags[1]) flags[4] = 'S';
	 if(TestFlag(r->tcp_flags,tcpflags[2]) == tcpflags[2]) flags[3] = 'R';
	 if(TestFlag(r->tcp_flags,tcpflags[3]) == tcpflags[3]) flags[2] = 'P';
	 if(TestFlag(r->tcp_flags,tcpflags[4]) == tcpflags[4]) flags[1] = 'A';
	 if(TestFlag(r->tcp_flags,tcpflags[5]) == tcpflags[5]) flags[0] = 'U';

	 //procol
	 Proto_string(r->prot, proto);

	snprintf(s,1023,"%s.%03u\t%2.3f\t%s\t%s:%u\t->\t%s:%u\t%s\t%u\t%lu\t%lu\t%lu",
			datestr1,r->msec_first,duration,proto,as,r->srcport,ds,r->dstport,flags,r->tos,r->dPkts,r->dOctets,r->aggr_flows);
	s[strlen(s)] = '\n';

} // End of print_record


void readNFCap(int rfd,int file_index,uint32_t start,uint32_t end)
{
	data_block_header_t block_header;
	master_record_t master_record;
	master_record_t *p_mr = NULL;
	common_record_t *flow_record; // *in_buff;

	char *string;
	char toString[1024];
	int ret,done =0,i=0;


	memset(in_buff,0,BUFFSIZE);
	p_mr = (master_record_t *)flow_records[file_index].master;

	while (!done) {
		// get next data block from file
		ret = ReadBlock(rfd, &block_header, (void *) &in_buff, &string);

		switch (ret) {
			case NF_CORRUPT:
			case NF_ERROR:
				if (ret == NF_CORRUPT)
					fprintf(stderr, "Skip corrupt data file '%s': '%s'\n",
							GetCurrentFilename(), string);
				else
					fprintf(stderr, "Read error in file '%s': %s\n",
							GetCurrentFilename(), strerror(errno));
				// fall through - get next file in chain
			case NF_EOF:
				goto out ;
		}

		if (block_header.id != DATA_BLOCK_TYPE_2) {
			fprintf(stderr, "Can't process block type %u. Skip block.\n",
					block_header.id);
			continue;
		}

		flow_record = in_buff;
		for (i = 0; i < block_header.NumRecords; i++) {
			memset(toString,0,1024);

			if(unlikely(!p_mr)) {
				printf("**** p_mr is NULL!");
				goto out;
			}

			if (likely(flow_record->type == CommonRecordType)) {
				uint32_t map_id = flow_record->ext_map;
				if (unlikely(extension_map_list.slot[map_id] == NULL)) {
					snprintf(
							toString,
							1024,
							"Corrupt data file! No such extension map id: %u. Skip record",
							flow_record->ext_map);
					toString[1023] = '\0';
				} else {
					ExpandRecord_v2(flow_record,
							extension_map_list.slot[flow_record->ext_map],
							&master_record);
					// update number of flows matching a given map
					extension_map_list.slot[map_id]->ref_count++;

					if(!IS_OUT_TIME_INTERVAL(master_record.first,start,master_record.last,end)) {
						//aggiungo il record perche' cade nell'intervallo che mi interessa
						memcpy(p_mr,&master_record,sizeof(master_record_t));
						//incremento il contatore
						flow_records[file_index].total++;
						//sposto il puntatore
						p_mr++;
					}
				}
			} else if (flow_record->type == ExtensionMapType) {
				extension_map_t *map = (extension_map_t *) flow_record;
				Insert_Extension_Map(&extension_map_list, map);
			} else {
				fprintf(stderr, "Skip unknown record type %i\n",
						flow_record->type);
			}

			// Advance pointer by number of bytes for netflow record
			flow_record = (common_record_t *) ((pointer_addr_t) flow_record + flow_record->size);

		} // for all records

	} // while

out:
	return ;
}

static void sortAndProcessData(time_t startTime,time_t endTime,int *outfd)
{
	time_t start = 0,
			end = 0,
			ei = 0;

	int header_i = 0,
		fblk_i =0,
		cnt_done =0,
		open_files = 0;

	if(header_list.num_heads <= 0) {
	      printf("No file to process\n");
	      exit(EXIT_SUCCESS);
	}

    /* Initialize start and end time to the range determined by the files */
    start = header_list.headers[0]->first_seen;
    end = header_list.headers[header_list.num_heads-1]->last_seen;
    
    if(startTime)
       start = startTime;
    if(endTime)
       end = endTime;
	
	//read FILESBLK files at most
	/************************************************************************************************/
	/**** Si suppone che per leggere un blocco non sia necessario accedere piu' di FILESBLK file ****/
	/************************************************************************************************/
	for(fblk_i=0; fblk_i < FILESBLK ; fblk_i++,header_i++) {
		if(header_i >= header_list.num_heads)
			break;
		allocNextSortedFile(flow_records,header_list, fblk_i,header_i,start,end);
		open_files++;
	}

	ei = start + blksize;
	//set the number of file to read
	cnt_done = header_list.num_heads - header_i;

	/*
	 * finche' non ho raggiunto endTime
	 */
	while(ei <= end) {
		//process all record beetween time interval e(i-1) and e(i)
	      calc_stat_block(flow_records,ei,blksize,outfd);

	      ei += blksize;

		//check for completed files
		for(fblk_i=0; fblk_i < FILESBLK ; fblk_i++) {
			if(flow_records[fblk_i].fd != 0) {
				if((flow_records[fblk_i].consumed == flow_records[fblk_i].total) || (ei > end)) {
					printf("===========================\n");
					printf("*** File completed\n");

					freeSortedFile(&flow_records[fblk_i]);

					if(allocNextSortedFile(flow_records,header_list, fblk_i,header_i,start,end)) {
						printf("*** Remaining files to load: %d\n",cnt_done);
						cnt_done--;
						header_i++;
					}
					printf("===========================\n");
				}
			}
		}
	}
	if(nf_stat == HISTO_STATS) {
	      end_histo(outfd);
	}

	return;
}

int main(int argc, char **argv)
{
      uint16_t duration_block = 0;
	char *rfile= NULL, *Rfile= NULL, *Mdirs= NULL,*duration = NULL;
	time_t startTime =0 , endTime=0;
	struct tm st,et;
	char *out_file = "./out_txt";
	int outfd[] = {0,0,0,0};
	int c = 0;

	rfile = Rfile = Mdirs = NULL;
	while ((c = getopt(argc, argv, "L:r:M:R:s:e:d:b:K:B:Y:H:S:a:t:O:")) != EOF) {
		switch (c) {
		case 'h':
			usage(argv[0]);
			exit(0);
		break;
		case 'L':
			if (!InitLog("argv[0]", optarg))
				exit(255);
		break;
		case 'r':
			rfile = optarg;
			if (strcmp(rfile, "-") == 0)
				rfile = NULL;
		break;
		case 'M':
			Mdirs = optarg;
		break;
		case 'R':
			Rfile = optarg;
		break;
		case 's':
		      memset(&st,0,sizeof(struct tm));
	            setenv("TZ", "CEST-2", 1);
		      //setenv("TZ", "GMT0", 1);
		      tzset();
		      strptime(optarg, "%Y-%m-%d %H:%M:%S", &st);
			startTime = mktime(&st);
		break;
		case 'e':
		      memset(&et,0,sizeof(struct tm));
                  setenv("TZ", "CEST-2", 1);
		      //setenv("TZ", "GMT0", 1);
                  tzset();
                  strptime(optarg,"%Y-%m-%d %H:%M:%S", &et);
			endTime = mktime(&et);
		break;
		case 'b':
			blksize = (uint32_t) strtol( optarg,NULL,10);
		break;
		case 'd':
		      duration_block = 1;
		      duration = optarg;
		break;
		case 'K':
		    set_stat_func(KULLBACK_ENTROPY);
		    set_stat_params((uint16_t) strtol( optarg,NULL,10));
		    nf_stat = KULLBACK_ENTROPY;
		break;
		case 'B':
		   set_stat_func(BASIC_STATS);
               set_stat_params((uint16_t) strtol( optarg,NULL,10));
               nf_stat = BASIC_STATS;
		break;
		case 'Y':
		   set_stat_func(RENYI);
               set_stat_params((uint16_t) strtol( optarg,NULL,10));
               nf_stat = RENYI;
		break;
		case 'H':
               set_stat_func(HISTO_STATS);
               set_stat_params((uint16_t) strtol( optarg,NULL,10));
               nf_stat = HISTO_STATS;
		break;
		case 'S':
		   set_stat_func(SORT);
               set_stat_params((uint16_t) strtol( optarg,NULL,10));
               nf_stat = SORT;
		break;
		case 'a':
		   alpha =  atof(optarg);
		break;
		case 't':
		   threshold = atof(optarg);
		   break;
		case 'O':
		   out_file = optarg;
		break;
		default:
			usage(argv[0]);
			exit(0);
		}
	}

	if (rfile && Rfile) {
		fprintf(stderr,
				"-r and -R are mutually exclusive. Please specify either -r or -R\n");
		exit(255);
	}
	if (Mdirs && !(rfile || Rfile)) {
		fprintf(stderr,
				"-M needs either -r or -R to specify the file or file list. Add '-R .' for all files in the directories.\n");
		exit(255);
	}
	if(duration_block != 0) {
	      endTime = startTime;
	      endTime += strtol(duration,NULL,10)*blksize;
            printf("startime: %d\toutfile endtime:%d\n",startTime,endTime);
	}



	init_file_out(nf_stat,outfd,out_file);
	InitExtensionMaps(&extension_map_list);
	SetupInputFileSequence(Mdirs, rfile, Rfile, startTime, endTime);
      sortAndProcessData(startTime,endTime,outfd);

	if(outfd[0] > 0) close(outfd[0]);
      if(outfd[1] > 0) close(outfd[1]);
      if(outfd[2] > 0) close(outfd[2]);
      if(outfd[3] > 0) close(outfd[3]);

      return 0;
}

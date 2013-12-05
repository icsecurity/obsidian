#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/socket.h> /* for socket(), connect(), send(), and recv() */
#include <arpa/inet.h>  /* for sockaddr_in and inet_addr() */
#include <fcntl.h>

#include "nffile.h"
#include "nfStat.h"
#include "nfsort.h"

#define POW16 (65536)

static nfsort_array_t *current;
uint32_t curr_size = BUFFSIZE;
int fd = 0;

int
init_nfsort(void)
{
   current = (nfsort_array_t *) malloc(sizeof(nfsort_array_t));
   if(!current) {
         perror("malloc():: current");
         goto err;
   }
   current->data = (nfsort_data_t *) malloc(sizeof(nfsort_data_t )*BUFFSIZE);
   if(!current->data) {
         perror("malloc():: current->data");
         goto err;
   }
   current->size = 0;
   return 0;

err:
   if(current) {
         if(current->data) {
               free(current->data);
         }
         free(current);
   }
   return -1;

}

int
pre_nfsort(flowslist_t *flow_records,master_record_t master_record,int fblk_i)
{
//save record in current
   int last = 0;
   uint64_t first_seen =0,last_seen=0;

   nfsort_data_t newrecord;

   memset(&newrecord,0,sizeof(nfsort_data_t));
   last = current->size;

   if(last == curr_size) {
         //need more space
         curr_size += BUFFSIZE;
         current->data = (nfsort_data_t *) realloc(current->data,sizeof(nfsort_data_t)*curr_size);
         if(!current->data) {
               perror("realloc():: current");
               return -1;
         }
   }

  // newrecord.ts = master_record.first;
   newrecord.srcip = master_record.ip_union._v4.srcaddr;
   newrecord.dstip = master_record.ip_union._v4.dstaddr;
   newrecord.srcport = master_record.srcport;
   newrecord.dstport = master_record.dstport;
#ifdef EXT_SORT
   newrecord.aggr_flows = master_record.aggr_flows;
   newrecord.out_bytes = master_record.dOctets;
   newrecord.out_pkts = master_record.dPkts;

   first_seen = master_record.first;
  // printf("first_seen 1: %lu\n",first_seen);
   first_seen <<= 16;
   //printf("first_seen 2: %lu\n",first_seen);
   first_seen |= (uint64_t)(master_record.msec_first);
   //printf("first_seen 3: %lu\n",first_seen);


   last_seen = master_record.last;
   //printf("last_seen 1: %lu\n",last_seen);
   last_seen <<= 16;
   //printf("last_seen 2: %lu\n",last_seen);
   last_seen |=  (uint64_t)(master_record.msec_last);
   //printf("last_seen 3: %lu\n",last_seen);

   newrecord.duration =  round(((double)(last_seen-first_seen))/POW16);
   newrecord.duration = newrecord.duration == 0 ? 1 : newrecord.duration;

   //printf("first:%d.%d last:%d.%d ===> duration:%d\n",master_record.first,
   //      master_record.msec_first,master_record.last,master_record.msec_last,newrecord.duration);
#endif

#ifdef ANON_SORT
	newrecord.tcp_flags = master_record.tcp_flags;		
	newrecord.prot = master_record.prot;
    newrecord.tos = master_record.tos;
#endif
   /*printf("%d %d %d %d %d %u %u %u\n",
         newrecord.srcip,newrecord.dstip,
         newrecord.srcport,newrecord.dstport,
         newrecord.aggr_flows,newrecord.out_pkts,newrecord.out_bytes);
    */
   //add record
   memcpy(&(current->data[last]),&newrecord,sizeof(nfsort_data_t));
   current->size++;

   flow_records[fblk_i].consumed++;

   return 0;
}

int
post_nfsort(time_t first,uint16_t msec_first,int *outfd)
{
   char datestr[64];
   char outfile[MAXPATHLEN];
   struct tm *ts;
   int nw = 0,size = 0,remaining = 0;

   ts = localtime(&first);
   memset(datestr,0,64);
   strftime(datestr, 63, "%Y-%m-%d-%H-%M", ts);

   memset(outfile,0,MAXPATHLEN);
   strncat(outfile,"sorted/",7);
   strncat(outfile,datestr,64);

   static int nf = 0;

   nf +=current->size;
   //printf("%s %d\n",datestr,nf);

   //printf("%s\n",outfile);
   fd = open(outfile, O_RDWR |O_CREAT | O_APPEND,0777);
   if(!fd) {
         perror("post_nfsort::open()");
         return -1;
   }

   size = sizeof(nfsort_data_t)*(current->size);

   remaining = size;
   do {
         nw = write(fd,current->data + nw,remaining);
         //printf("nw: %d size:%d\n",nw,size);
         remaining -= nw;
   }while(remaining > 0);

   if(current) {
         if(current->data)
            free(current->data);
         free(current);
   }
   curr_size = BUFFSIZE;
   close(fd);

   return 0;
}

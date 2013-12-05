#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/types.h>

#include "nffile.h"
#include "nfStat.h"
#include "basic_stats.h"

#define MEGABYTES(x) (x>>20)


stat_array_t *current;
b_data_array_t *blist;

int
init_basic_stats(void)
{
   current = (stat_array_t *) malloc(sizeof(stat_array_t));
   if(!current) {
         perror("current malloc()");
         goto err;
   }

   current->data = (data_stat_t *) malloc(sizeof(data_stat_t)*BUFFSIZE);
   if(!current->data) {
         perror("current->data malloc()");
         goto err;
   }
   current->size = 0;

   blist = (b_data_array_t *) malloc(sizeof(b_data_array_t));
   if(!blist) {
         perror("blist malloc()");
         goto err;
   }
   blist->data =(b_data_stat_t*) malloc(sizeof(b_data_stat_t)*BUFFSIZE);
   if(!blist->data) {
         perror("blist->data malloc()");
         goto err;
   }
   blist->size = 0;

   return 0;

err:
      //block analisys
      if(current) {
            if(current->data)
               free(current->data);
            free(current);
      }

      if(blist) {
            if(blist->data)
               free(blist->data);
            free(blist);
      }
      return -1;
}

int
pre_basic_stats(flowslist_t *flow_records,master_record_t master_record,int fblk_i)
{
   int id = 0;
   static uint32_t curr_size = BUFFSIZE;

   id = func.search_field_value(master_record,current);
   if( id == -1) {
         if(current->size == curr_size) {
               //need more space
               curr_size += BUFFSIZE;
               current->data = (data_stat_t *) realloc(current->data,sizeof(data_stat_t)*curr_size);
               if(!current->data) {
                     perror("realloc current->data ");
                     return -1;
               }
               blist->data = (b_data_stat_t*) realloc( blist->data,sizeof(b_data_stat_t)*curr_size);
               if(!blist->data){
                     perror("realloc blist->data ");
                     return -1;
               }
         }
         //add record by key
         func.add_new_key(master_record,current,current->size);

         //set basic stats data
         blist->data[current->size].aggr_flows = master_record.aggr_flows;
         blist->data[current->size].out_bytes = master_record.dOctets;
         blist->data[current->size].out_pkts = master_record.dPkts;

         current->size++;

   } else {
         current->data[id].cnts++;

         blist->data[id].aggr_flows += master_record.aggr_flows;
         blist->data[id].out_bytes += master_record.dOctets;
         blist->data[id].out_pkts += master_record.dPkts;
   }

   flow_records[fblk_i].consumed++;

   return 0;

}

int
post_basic_stats(time_t first,uint16_t msec_first,int *outfd)
{
   int i=0;
   char datestr[64],outstr[128];
   struct tm *ts;

   ts = localtime(&first);
   memset(datestr,0,64);
   strftime(datestr, 63, "%Y-%m-%d %H:%M:%S", ts);

   //do stats
   for(i = 0; i < current->size; i++) {
         memset(outstr,0,128);
         sprintf(outstr,"%s.%03u %lu %lu %lu\n",datestr,msec_first,
               blist->data[i].aggr_flows,blist->data[i].out_bytes,blist->data[i].out_pkts);
         write(outfd[0],outstr,strlen(outstr));
   }

}

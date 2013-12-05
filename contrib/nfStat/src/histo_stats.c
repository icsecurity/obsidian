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


#include "histo_stats.h"
#include "nffile.h"
#include "nfStat.h"

stat_array_t *current;

int
init_histo(void)
{
   if(!current) {
      current = (stat_array_t *) malloc(sizeof(stat_array_t));
      if(!current) {
            perror("malloc():: current");
            goto err;
      }
      current->data = (data_stat_t *) malloc(sizeof(data_stat_t)*BUFFSIZE);
      if(!current->data) {
            perror("malloc():: current->data");
            goto err;
      }
      current->size = 0;
   }
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
pre_histo(flowslist_t *flow_records,master_record_t master_record,int fblk_i)
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
                     perror("realloc():: current");
                     return -1;
               }
         }

         //add record by key
         func.add_new_key(master_record,current,current->size);
         current->size++;

   } else {
         current->data[id].cnts++;
   }

   flow_records[fblk_i].consumed++;

   return 0;

}

int
histo_freq_cmp(const void *fa, const void *fb)
{
   data_stat_t *ma = (data_stat_t *) fa;
   data_stat_t *mb = (data_stat_t *) fb;

   //inverted order
   return mb->cnts - ma->cnts;
}

int
post_histo(time_t first,uint16_t msec_first,int *outfd)
{

   qsort(current->data,current->size,sizeof(data_stat_t),histo_freq_cmp);

   return 0;
   /*

   int half = 0,k1 = 0,k2 = 0;

   half = current->size/2;
   k1 = half +1;
   k2 = current->size - (k1);

   //sort ip by frequency
   #pragma omp parallel
   {
               #pragma omp sections
               {
                     #pragma omp section
                     qsort(current->data,k1,sizeof(data_stat_t),histo_freq_cmp);
                     #pragma omp section
                     qsort(current->data+k1 ,k2,sizeof(data_stat_t),histo_freq_cmp);
               }
   }*/

}

int end_histo(int *outfd)
{
   int i = 0;
   char outstr[128];
   char ip_addr[40];

   for(i = 0; i < current->size; i++) {
         current->data[i].key1 = htonl(current->data[i].key1);
         inet_ntop(AF_INET, &current->data[i].key1, ip_addr, sizeof(ip_addr));
         ip_addr[40 - 1] = 0;

         //write data in entropy output file
         memset(outstr,0,128);
         sprintf(outstr,"\"%s\",%u\n",ip_addr,current->data[i].cnts);
         write(outfd[0],outstr,strlen(outstr));
   }

   return 0;
}

/*
 * stats.c
 *
 *  Created on: 20/apr/2011
 *      Author: antonio
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/types.h>
#include <fcntl.h>

#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif

#include "nffile.h"
#include "nfStat.h"

#include "stats_common.h"
#include "kullback_entropy.h"
#include "basic_stats.h"
#include "renyi.h"
#include "histo_stats.h"
#include "nfsort.h"

//struct stats_func func;

void
calc_stat_block(flowslist_t *flow_records, uint32_t ei,uint32_t blksize,int *outfd)
{
   master_record_t master_record;
   uint64_t consumed = 0, total = 0;
   static uint16_t msec_first =0 ;
   static time_t first = 0;
   int done = 0, fblk_i = 0;

   //init_stat
   func.initprocess_block();
   //loop
   while (!done)
      {
         done = 1;
         //read FILESBLK files at most
         for (fblk_i = 0; fblk_i < FILESBLK; fblk_i++)
            {
               if (flow_records[fblk_i].fd != 0)
                  {
                     consumed = flow_records[fblk_i].consumed;
                     total = flow_records[fblk_i].total;

                     if (consumed < total)
                        {
                           master_record = flow_records[fblk_i].master[consumed];

                           //per ogni record nell'intervallo
                           if (master_record.first <= ei) {
                                 if(!first) {
                                       first = master_record.first;
                                       msec_first = master_record.msec_first;
                                 }
                                 done = 0;
                                 //pre_process
                                 func.preprocess_block(flow_records,master_record,fblk_i);
                            }

                        }
                   }
            }
     }
   //post_process
   func.postprocess_block(first, msec_first,outfd);
   first += blksize;

   return ;
}

void
set_stat_func(uint16_t stat)
{
   switch(stat) {
      case KULLBACK_ENTROPY:
         func.initprocess_block = init_kullback_entropy;
         func.preprocess_block = pre_kullback_entropy;
         func.postprocess_block = post_kullback_entropy;
         break;
      case RENYI:
         func.initprocess_block = init_renyi;
         func.preprocess_block = pre_renyi;
         func.postprocess_block = post_renyi;
         break;
      case BASIC_STATS:
         func.initprocess_block = init_basic_stats;
         func.preprocess_block = pre_basic_stats;
         func.postprocess_block = post_basic_stats;
         break;
      case HISTO_STATS:
         func.initprocess_block = init_histo;
         func.preprocess_block = pre_histo;
         func.postprocess_block = post_histo;
         break;
      case SORT:
         func.initprocess_block = init_nfsort;
         func.preprocess_block = pre_nfsort;
         func.postprocess_block=post_nfsort;
      break;
      default:
         func.initprocess_block = init_basic_stats;
         func.preprocess_block = pre_basic_stats;
         func.postprocess_block = post_basic_stats;
      break;
   }

   return ;
}

void
set_stat_params(uint16_t opt)
{
   switch(opt) {
      case NONE:
         printf("*** Search by NONE\n");
         func.search_field_value = search_by_none;
         func.add_new_key = add_by_none;
      break;
      case SRCIP:
         printf("*** Search by SRCIP\n");
         func.search_field_value = search_by_srcip;
         func.add_new_key = add_by_srcip;
         break;
      case DSTIP:
         printf("*** Search by DSTIP\n");
         func.search_field_value = search_by_dstip;
         func.add_new_key = add_by_dstip;
         break;
      case SRCIP_SRCPORT:
         printf("*** Search by SRCIP_SRCPORT\n");
         func.search_field_value = search_by_srcip_port;
         func. add_new_key = add_by_srcip_port;
         break;
      case DSTIP_DSTPORT:
         printf("*** Search by DSTIP_DSTPORT\n");
         func.search_field_value = search_by_dstip_port;
         func.add_new_key = add_by_dstip_port;
         break;
      default:
         printf("*** Search by DSTIP\n");
         func.search_field_value = search_by_dstip;
         func.add_new_key = add_by_dstip;
      break;
   }

   return;
}



int
search_by_dstip_port(master_record_t master_record,stat_array_t *array)
{
   int i = 0,ret = -1;

   register uint64_t r1 = 0;
   uint64_t *p= NULL;

   r1 = master_record.dstport;
   r1 = r1 << 32;
   r1 |= master_record.ip_union._v4.dstaddr;

   for(i=0; i < array->size;i++) {
         p=(uint64_t *) (&(array->data[i].key1));

         if((*p) == r1)
            {
               ret = i;
               break;
            }
   }
   return ret;
}

//TODO: inserimento ordinato!!!
void
add_by_dstip_port(master_record_t master_record,stat_array_t *array,int where)
{
   uint64_t r1 = 0;

   r1 = master_record.dstport;
   r1 = r1 << 32;
   r1 |= master_record.ip_union._v4.dstaddr;

   array->data[where].key1 = r1;
   array->data[where].cnts = 1;
}

int
search_by_dstip(master_record_t master_record,stat_array_t *array)
{
   uint64_t key = (uint64_t) master_record.ip_union._v4.dstaddr;
   int i = 0;

   for(i=0; i < array->size;i++) {
       if(array->data[i].key1 == key)
          return i; //found
   }

   return -1;
}

void
add_by_dstip(master_record_t master_record,stat_array_t *array,int where)
{
   uint32_t key = master_record.ip_union._v4.dstaddr;

   array->data[where].key1 = key;
   array->data[where].cnts = 1;
}

int
search_by_srcip(master_record_t master_record,stat_array_t *array)
{
   uint64_t key = (uint64_t) master_record.ip_union._v4.srcaddr;
   int i = 0;

   for(i=0; i < array->size;i++) {
       if(array->data[i].key1 == key)
          return i; //found
   }

   return -1;
}

void
add_by_srcip(master_record_t master_record,stat_array_t *array,int where)
{
   uint32_t key = master_record.ip_union._v4.srcaddr;

   array->data[where].key1 = key;
   array->data[where].cnts = 1;
}

int
search_by_srcip_port(master_record_t master_record,stat_array_t *array)
{
   int i = 0,ret = -1;

   register uint64_t r1 = 0;
   uint64_t *p= NULL;

   r1 = master_record.srcport;
   r1 = r1 << 32;
   r1 |= master_record.ip_union._v4.srcaddr;

   for(i=0; i < array->size;i++) {
         p=(uint64_t *) (&(array->data[i].key1));

         if((*p) == r1)
            {
               ret = i;
               break;
            }
   }
   return ret;
}

void
add_by_srcip_port(master_record_t master_record,stat_array_t *array,int where)
{
   uint64_t r1 = 0;

   r1 = master_record.srcport;
   r1 = r1 << 32;
   r1 |= master_record.ip_union._v4.srcaddr;

   array->data[where].key1 = r1;
   array->data[where].cnts = 1;
}

int
search_by_none(master_record_t master_record,stat_array_t *array)
{
   if(array->size == 0) return -1;

   return 0;

}

void
add_by_none(master_record_t master_record,stat_array_t *array,int where)
{
   return;
}

void
init_file_out(int stat,int *outfd,char *out_file)
{
   char stat_out_file[MAXPATHLEN];

   switch(stat)
   {
      case KULLBACK_ENTROPY:
         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[0] = open(strncat(stat_out_file,"_kullback",10),O_WRONLY | O_CREAT | O_TRUNC,0777);
         if(!outfd[0]) {
               perror("Can't open output file ");
               exit(EXIT_FAILURE);
         }

         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[1] = open(strncat(stat_out_file,"_entropy",10),O_WRONLY | O_CREAT | O_TRUNC,0777);

         if(!outfd[1]) {
               perror("Can't open output file ");
               exit(EXIT_FAILURE);
         }

         memset(stat_out_file,0,256);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[2] = open(strncat(stat_out_file,"_kullback_inv",13),O_WRONLY | O_CREAT | O_TRUNC,0777);
         if(!outfd[2]) {
               perror("Can't open output file ");
               exit(EXIT_FAILURE);
         }

         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[3] = open(strncat(stat_out_file,"_threshold",10),O_WRONLY | O_CREAT | O_TRUNC,0777);
         if(!outfd[3]) {
               perror("Can't open output file ");
               exit(EXIT_FAILURE);
         }
      break;
      case BASIC_STATS:
         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[0] = open(strncat(stat_out_file,"_basic",10),O_WRONLY | O_CREAT | O_TRUNC,0777);
         if(!outfd[0]) {
             perror("Can't open output file ");
             exit(EXIT_FAILURE);
         }
         outfd[1] = -1;
      break;
      case RENYI:
         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[0] = open(strncat(stat_out_file,"_renyi",10),O_WRONLY | O_CREAT| O_TRUNC,0777);
         if(!outfd[0]) {
             perror("Can't open output file ");
             exit(EXIT_FAILURE);
         }
         outfd[1] = -1;
      break;
      case HISTO_STATS:
         memset(stat_out_file,0,MAXPATHLEN);
         strncpy(stat_out_file,out_file,MAXPATHLEN-10);
         outfd[0] = open(strncat(stat_out_file,"_histo",10),O_WRONLY | O_CREAT| O_TRUNC,0777);
         if(!outfd[0]) {
             perror("Can't open output file ");
             exit(EXIT_FAILURE);
         }
         outfd[1] = -1;
      break;
      case SORT:
         //nothing to do
      break;
      default:
         perror("Statistical Unknown\n");
         exit(EXIT_FAILURE);
   }


}



#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/types.h>


#include "renyi.h"
#include "nffile.h"
#include "nfStat.h"

float alpha = 0.9;

stat_array_t *memory;
stat_array_t *current;
stat_array_t *intersect;

int
init_renyi(void)
{
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
pre_renyi(flowslist_t *flow_records,master_record_t master_record,int fblk_i)
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
post_renyi(time_t first,uint16_t msec_first,int *outfd)
{
   uint64_t *p1 = NULL;
   uint64_t *p2= NULL;
   uint32_t inter_size = 0,curr_freq =0,mem_freq = 0,mem_card = 0;

   double pi=0.0,qi =0.0,sum=0.0,result=0.0;
   int i=0,j=0,k=0;
   char datestr[64],outstr[128];
   struct tm *ts;

   ts = localtime(&first);
   memset(datestr,0,64);
   strftime(datestr, 63, "%Y-%m-%d %H:%M:%S", ts);

   //intersect memory and current
   if(memory) {
      inter_size = MIN(memory->size,current->size);

      intersect = (stat_array_t *)malloc(sizeof(stat_array_t));
      if(!intersect) {
            perror("malloc():: intersect");
            return -1;
      }
      intersect->data = (data_stat_t*) malloc(sizeof(data_stat_t) * inter_size);
      if(!intersect->data) {
            perror("malloc():: intersect->data");
            return -1;
      }
      intersect->size = 0;

      //intersect memory and current
       for(i=0; i < memory->size;i++) {
            p1 = (uint64_t *) (&(memory->data[i].key1));
            for(j=0; j < current->size;j++) {
                  p2=(uint64_t *) (&(current->data[j].key1));
                  if((*p2)==(*p1))
                     {
                        intersect->data[k].key1 =  current->data[j].key1;
                        intersect->data[k].cnts = current->data[j].cnts;
                        intersect->data[k].cnts_mem = memory->data[i].cnts;

                        curr_freq += intersect->data[k].cnts;
                        mem_freq += intersect->data[k].cnts_mem;

                        k++;

                        break;
                  }
            }
            mem_card += memory->data[i].cnts;
      }

      intersect->size = k;

      for(i=0; i < k;i++)
          {
             pi = ((double)intersect->data[i].cnts)/curr_freq;
             qi = ((double)intersect->data[i].cnts_mem )/mem_freq;
             sum += pow(pi,alpha)*pow(qi,1-alpha);
          }
       result= (1/(alpha-1)) * LOG2(sum);
       //write data renyi in output file
       memset(outstr,0,128);
       sprintf(outstr,"%s.%03u,%.12f\n",datestr,msec_first,result);
       write(outfd[0],outstr,strlen(outstr));

      //free old memory
      if(memory) {
            free(memory->data);
            free(memory);
      }
      if(intersect) {
            free(intersect->data);
            free(intersect);
      }
   }
   //update memory
   memory = current;

   return 0;
}

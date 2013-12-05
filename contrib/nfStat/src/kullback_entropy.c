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



#include "kullback_entropy.h"
#include "nffile.h"
#include "nfStat.h"
//#define DEBUG

stat_array_t *memory;
stat_array_t *current;
stat_array_t *intersect;
uint32_t curr_card = 0;
double old_kullback=0.0;
double threshold = 1.0;

int
init_kullback_entropy(void)
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
pre_kullback_entropy(flowslist_t *flow_records,master_record_t master_record,int fblk_i)
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

   curr_card++;
   flow_records[fblk_i].consumed++;

   return 0;
}

int
post_kullback_entropy(time_t first,uint16_t msec_first,int *outfd)
{
   uint64_t *p1 = NULL;
   uint64_t *p2= NULL;
   uint32_t inter_size = 0,curr_freq =0,mem_freq = 0;
   uint32_t maxip;

   double pi=0.0,qi =0.0,sum=0.0,entropy=0.0,sum_inv=0.0,maxpi=0.0;
   int i=0,j=0,k=0;
   char datestr[64],outstr[128];
   char ip_addr[40];
   struct tm *ts;

   //dump mode switch
   static int dump_mode = 0;

   ts = localtime(&first);
   memset(datestr,0,64);
   strftime(datestr, 63, "%Y-%m-%d %H:%M:%S", ts);

   #ifdef DEBUG
   printf("[SUMMARY ENTROPY] %d\n",curr_card);
   #endif
   //calculate entropy
   for(i=0 ; i < current->size; i++)
      {
         pi = ((double)current->data[i].cnts)/curr_card;

         #ifdef DEBUG
         current->data[i].key1 = htonl(current->data[i].key1);
         inet_ntop(AF_INET, &current->data[i].key1, ip_addr, sizeof(ip_addr));
         ip_addr[40 - 1] = 0;
         printf("[ENTROPY] %s %s %f\n",datestr,ip_addr,pi);
         #endif
         entropy += pi*LOG2(pi);
      }
   //write data in entropy output file
   memset(outstr,0,128);
   sprintf(outstr,"%s.%03u,%.12f\n",datestr,msec_first,entropy*(-1));
   write(outfd[ENTROPY],outstr,strlen(outstr));
   curr_card=0;

   //if(old_entropy == 0) old_entropy = entropy;

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
       for(i=0; i < memory->size;i++)
          {
            p1 = (uint64_t *) (&(memory->data[i].key1));

            for(j=0; j < current->size;j++)
               {
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
      }
      intersect->size = k;

#ifdef DEBUG
      printf("[SUMMARY KULLBACK] %d %d %d\n",mem_freq,curr_freq,k);
#endif
      //calculate kullback
      for(i=0; i < k;i++)
         {
            pi = ((double)intersect->data[i].cnts)/curr_freq;
            qi = ((double)intersect->data[i].cnts_mem )/mem_freq;

            //if(maxpi < pi){
            //      maxpi = pi;
            //      maxip = intersect->data[i].key1;
            //}
#ifdef DEBUG

            //PRINTF TS, IP , PI
            intersect->data[i].key1 = htonl(intersect->data[i].key1);
            inet_ntop(AF_INET, &intersect->data[i].key1, ip_addr, sizeof(ip_addr));
            ip_addr[40 - 1] = 0;

            printf("[KULLBACK] %s %s %f %f\n",datestr,ip_addr,pi,qi);
#endif
            sum += pi*LOG2(pi/qi);
            sum_inv += qi*LOG2(qi/pi);
         }

      //maxip = htonl(maxip);
      //inet_ntop(AF_INET, &maxip, ip_addr, sizeof(ip_addr));
      //ip_addr[40 - 1] = 0;
      //printf("threshold: %f sum: %f\n",threshold,sum);

      if(dump_mode > 0){
            dump_mode--;
            complete_dump(datestr,curr_freq,mem_freq,dump_mode);
      }
      else if(sum > threshold) {
            dump_mode = 10;
            //complete dump
            complete_dump(datestr,curr_freq,mem_freq,dump_mode);
      }


      //write data kullback in output file
      memset(outstr,0,128);
      sprintf(outstr,"%s.%03u,%.12f\n",datestr,msec_first,sum);
      write(outfd[KULLBACK],outstr,strlen(outstr));

      //write data kullback_INV in output file
      memset(outstr,0,128);
      sprintf(outstr,"%s.%03u,%.12f\n",datestr,msec_first,sum_inv);
      write(outfd[KULLBACK_INV],outstr,strlen(outstr));

      //write data threshold in output file
      memset(outstr,0,128);
      sprintf(outstr,"%s.%03u,%.12f\n",datestr,msec_first,entropy*old_kullback*(-1));
      write(outfd[THRESHOLD],outstr,strlen(outstr));

      //free old memory
      if(memory) {
            free(memory->data);
            free(memory);
            memory = NULL;
      }
      if(intersect) {
            free(intersect->data);
            free(intersect);
            intersect = NULL;
      }
      old_kullback = sum;
   }
   //update memory
   memory = current;

   return 0;
}

void
complete_dump(char *datestr,uint32_t curr_freq,uint32_t mem_freq,int dump_mode)
{
   int fd;
   char outstr[128];
   char ip_addr[40];
   int i = 0;
   double pi=0.0,qi=0.0,component = 0.0;

   static char fname[64];

   if(dump_mode == 10) {
         int len = strlen(datestr);

         memset(fname,0,64);
         strncat(fname,datestr,len);
         strncat(fname,"_anomaly",64-len-1);
   }
   fd = open(fname, O_WRONLY | O_CREAT | O_APPEND,0777);
   if(fd == -1) {
         perror("complete_dump()::open() failed");
         return;
   }

   for(i=0; i < intersect->size; i++) {
         pi = ((double)intersect->data[i].cnts)/curr_freq;
         qi = ((double)intersect->data[i].cnts_mem )/mem_freq;
         component = pi*LOG2(pi/qi);

         intersect->data[i].key1 = htonl(intersect->data[i].key1);
         inet_ntop(AF_INET, &intersect->data[i].key1, ip_addr, sizeof(ip_addr));
         ip_addr[40 - 1] = 0;

         memset(outstr,0,128);
         sprintf(outstr,"%s %.12f %d\n",ip_addr,component,10-dump_mode);
         write(fd,outstr,strlen(outstr));
   }

   close(fd);
   return;
}

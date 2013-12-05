/*
 * stats.h
 *
 *  Created on: 20/apr/2011
 *      Author: antonio
 */

#ifndef STATS_H_
#define STATS_H_

#include <stdint.h>
#include "util.h"

#define LOG2(a) ((logf(a))/(0.693147182465))

enum
{
   NONE,SRCIP, DSTIP, SRCIP_SRCPORT,DSTIP_DSTPORT
};

enum
{
   KULLBACK_ENTROPY,RENYI,BASIC_STATS,HISTO_STATS,SORT
};

typedef struct data_stat_s {
   uint64_t key1; //first and second key
   //uint64_t key2; //third and fourth key

   uint32_t cnts; //value
   uint32_t cnts_mem; //counter of the past value
} data_stat_t;

typedef struct stat_array_s {
   uint32_t size; //elems of each array
   uint32_t pad;
   data_stat_t *data;
} stat_array_t;

struct stats_func {
   int
   (*initprocess_block)(void);
   int
   (*preprocess_block)(flowslist_t *flow_records,master_record_t master_record,int fblk_i);
   int
   (*postprocess_block)(time_t first,uint16_t msec_first,int *outfd);

   int
   (*search_field_value)(master_record_t master_record,stat_array_t *array);
   void
   (*add_new_key)(master_record_t record,stat_array_t *data,int where);
}func;

void
calc_stat_block(flowslist_t *flow_records, uint32_t ei,uint32_t blksize,int *outfd);

void
set_stat_func(uint16_t stat);

void
set_stat_params(uint16_t opt);

int
search_by_dstip(master_record_t master_record,stat_array_t *array);

void
add_by_dstip(master_record_t master_record,stat_array_t *array,int where);

int
search_by_dstip_port(master_record_t master_record,stat_array_t *array);

void
add_by_dstip_port(master_record_t master_record,stat_array_t *array,int where);

int
search_by_srcip(master_record_t master_record,stat_array_t *array);

void
add_by_srcip(master_record_t master_record,stat_array_t *array,int where);

int
search_by_srcip_port(master_record_t master_record,stat_array_t *array);

void
add_by_srcip_port(master_record_t master_record,stat_array_t *array,int where);

int
search_by_none(master_record_t master_record,stat_array_t *array);

void
add_by_none(master_record_t master_record,stat_array_t *array,int where);

void
init_file_out(int stat,int *outfd,char *out_file);

#endif /* STATS_H_ */

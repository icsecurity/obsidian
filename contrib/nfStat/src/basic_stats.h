/*
 * basic_stat.h
 *
 *  Created on: 20/apr/2011
 *      Author: antonio
 */

#ifndef BASIC_STAT_H_
#define BASIC_STAT_H_

//#include "util.h"
#include "stats_common.h"

typedef struct b_data_stat_s {
   uint64_t    out_pkts;
   uint64_t    out_bytes;
   uint64_t    aggr_flows;
} b_data_stat_t;

typedef struct b_data_s {
   uint32_t size; //elems of each array
   uint32_t padding; //64bit addressing
   b_data_stat_t *data;
} b_data_array_t;

int
init_basic_stats(void);

int
pre_basic_stats(flowslist_t *flow_records,master_record_t master_record,int fblk_i);

int
post_basic_stats(time_t first,uint16_t msec_first,int *outfd);

#endif /* BASIC_STAT_H_ */

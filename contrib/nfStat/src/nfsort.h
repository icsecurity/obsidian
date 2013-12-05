/*
 * nfsort.h
 *
 *  Created on: 30/apr/2011
 *      Author: antonio
 */

#ifndef NFSORT_H_
#define NFSORT_H_

#include <time.h>

#include "stats_common.h"

#define EXT_SORT (1)
#define ANON_SORT (1)

typedef struct nfsort_data_s {
#ifdef EXT_SORT
   uint64_t aggr_flows;
   uint64_t out_bytes;
   uint64_t out_pkts;
   uint32_t duration;
#endif
#ifdef ANON_SORT
	uint8_t tcp_flags;		
	uint8_t	prot;
    uint8_t	tos;
#endif
   uint32_t srcip;
   uint32_t dstip;
   uint16_t srcport;
   uint16_t dstport;

   //uint32_t padding;
} nfsort_data_t;

typedef struct nfsort_array_s {
   nfsort_data_t *data;
   uint32_t size; //elems of each array
   uint32_t pad;
} nfsort_array_t;



int
init_nfsort(void);

int
pre_nfsort(flowslist_t *flow_records,master_record_t master_record,int fblk_i);

int
post_nfsort(time_t first,uint16_t msec_first,int *outfd);


#endif /* NFSORT_H_ */

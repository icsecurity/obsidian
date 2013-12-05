/*
 * histo_stats.h
 *
 *  Created on: 27/apr/2011
 *      Author: antonio
 */

#ifndef HISTO_STATS_H_
#define HISTO_STATS_H_

#include "stats_common.h"

int
init_histo(void);

int
pre_histo(flowslist_t *flow_records,master_record_t master_record,int fblk_i);

int
post_histo(time_t first,uint16_t msec_first,int *outfd);

int
end_histo(int *outfd);

#endif /* HISTO_STATS_H_ */

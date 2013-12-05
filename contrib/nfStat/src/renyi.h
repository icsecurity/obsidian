/*
 * renyi.h
 *
 *  Created on: 22/apr/2011
 *      Author: antonio
 */

#ifndef RENYI_H_
#define RENYI_H_

#include "stats_common.h"

int
init_renyi(void);

int
pre_renyi(flowslist_t *flow_records,master_record_t master_record,int fblk_i);

int
post_renyi(time_t first,uint16_t msec_first,int *outfd);


#endif /* RENYI_H_ */

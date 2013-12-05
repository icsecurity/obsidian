#ifndef KULLBACK_H_
#define KULLBACK_ENTROPY_H_

#include "stats_common.h"

#define KULLBACK 0
#define ENTROPY 1
#define KULLBACK_INV 2
#define THRESHOLD 3

int
init_kullback_entropy(void);

int
pre_kullback_entropy(flowslist_t *flow_records,master_record_t master_record,int fblk_i);

int
post_kullback_entropy(time_t first,uint16_t msec_first,int *outfd);

void
complete_dump(char *datestr,uint32_t curr_freq,uint32_t mem_freq,int dump_mode);


#endif

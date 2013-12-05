/*
 * nfStat.h
 *
 *  Created on: 04/apr/2011
 *      Author: antonio
 */

#ifndef NFSTAT_H_
#define NFSTAT_H_

#define FILESBLK (10)
#define FILEDAY (289)

#define DEFAULT_BLK_SIZE (60)

#define BUFFSIZE (1048576)
#define MAX_BUFFER_SIZE (104857600)

#define likely(x)       __builtin_expect((x),1)
#define unlikely(x)     __builtin_expect((x),0)


#endif /* NFSTAT_H_ */

/*
 *  Copyright (c) 2009, Peter Haag
 *  Copyright (c) 2004-2008, SWITCH - Teleinformatikdienste fuer Lehre und Forschung
 *  All rights reserved.
 *  
 *  Redistribution and use in source and binary forms, with or without 
 *  modification, are permitted provided that the following conditions are met:
 *  
 *   * Redistributions of source code must retain the above copyright notice, 
 *     this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above copyright notice, 
 *     this list of conditions and the following disclaimer in the documentation 
 *     and/or other materials provided with the distribution.
 *   * Neither the name of SWITCH nor the names of its contributors may be 
 *     used to endorse or promote products derived from this software without 
 *     specific prior written permission.
 *  
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
 *  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
 *  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
 *  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
 *  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
 *  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 *  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 *  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
 *  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
 *  POSSIBILITY OF SUCH DAMAGE.
 *  
 *  $Author: haag $
 *
 *  $Id: util.h 39 2009-11-25 08:11:15Z haag $
 *
 *  $LastChangedRevision: 39 $
 *	
 */

#include "nffile.h"

#ifndef _UTIL_H
#define _UTIL_H 1

#define FILE_ERROR -1
#define EMPTY_LIST -2

#define EBUFF_SIZE 256

#ifdef WORDS_BIGENDIAN
#	define ntohll(n)	(n)
#	define htonll(n)	(n)
#else
#	define ntohll(n)	(((uint64_t)ntohl(n)) << 32) + ntohl((n) >> 32)
#	define htonll(n)	(((uint64_t)htonl(n)) << 32) + htonl((n) >> 32)
#endif

//contains the names of all
//the files to process
typedef struct stringlist_s {
	uint32_t	block_size;
	uint32_t	max_index;
	uint32_t	num_strings;
	char		**list;
} stringlist_t;

//contains the headers of all
//the file to process
typedef struct headerlist_s {
	uint32_t num_heads;
	uint32_t max_heads;
	stat_record_t **headers;
} headerlist_t;

typedef struct flowslist_s {
	int fd;
	uint64_t total;
	uint64_t consumed;
	master_record_t *master;
} flowslist_t;

typedef struct masterlist_s {
	master_record_t *r;
	master_record_t *next;
} masterlist_t;

void xsleep(long sec);

int InitLog(char *name, char *facility);

void LogError(char *format, ...);

void LogInfo(char *format, ...);

void InitStringlist(stringlist_t *list, int block_size);

void InsertString(stringlist_t *list, char *string);

void DeleteString(stringlist_t *list, int i) ;

void InitHeaderList(headerlist_t *list,int num_entry);

void InsertHeaderList(headerlist_t *list,stat_record_t *stat_ptr);

master_record_t *InitFlowList( uint64_t num_entry);

int allocNextSortedFile(flowslist_t *flow_records,headerlist_t header_list,
							int fblk_i,int header_i,uint32_t start,uint32_t end);

void freeSortedFile(flowslist_t *flow_record);

int ScanTimeFrame(char *tstring, time_t *t_start, time_t *t_end);

char *TimeString(time_t start, time_t end);

char *UNIX2ISO(time_t t);

time_t ISO2UNIX(char *timestring);

void SetupInputFileSequence(char *multiple_dirs, char *single_file, char *multiple_files,time_t startime,time_t endTime);

char *GetCurrentFilename(void);

void Setv6Mode(int mode);

int qsortCompare(const void *fa, const void *fb);

master_record_t * merge_flows(master_record_t *l1,int k1,master_record_t *l2, int k2);

//return true if the interval [s1-e1] doesn't intersect with [s2-e2]
//#define IS_OUT_TIME_INTERVAL(s1,s2,e1,e2)    \
			((!(((s1 >= s2) && (s1 <= e2))|| \
		    ((e1 <= e2) &&(e1 >= s2)))) &&   \
		    (!((s1 < s2) && (e1 > e2))) )

#define IS_OUT_TIME_INTERVAL(s1,s,e1,e) \
		                (!(((s1 >= s)&&(s1 <= e)) || ((e1 >= s) && (e1 <= e)) || ((s1 <= s) && (e1 >= e)) ))

#endif //_UTIL_H

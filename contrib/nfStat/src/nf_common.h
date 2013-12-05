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
 *  $Id: nf_common.h 39 2009-11-25 08:11:15Z haag $
 *
 *  $LastChangedRevision: 39 $
 *	
 *
 */

#ifndef _NF_COMMON_H
#define _NF_COMMON_H 1


typedef void (*printer_t)(void *, char **, int);

#if ( SIZEOF_VOID_P == 8 )
typedef uint64_t	pointer_addr_t;
#else
typedef uint32_t	pointer_addr_t;
#endif

typedef struct msec_time_s {
	time_t		sec;
	uint16_t	msec;
} msec_time_tt;

/* common minimum netflow header for all versions */
typedef struct common_flow_header {
  uint16_t  version;
  uint16_t  count;
} common_flow_header_t;

/* buffer size issues */

// 100MB max buffer size when dynamically extending
#define MAX_BUFFER_SIZE 104857600	

/* input buffer size, to read data from the network */
#define NETWORK_INPUT_BUFF_SIZE 65535	// Maximum UDP message size

/* output buffer size, tmp buffer, before writing data to the file 
 * when this buffer is 85% full, it gets written to disk.
 * no read cycle must ever produce more output data than it reads from the network
 * so 8,5 MB + 1 MB = 9.5MB of 10MB
 */
#define BUFFSIZE 1048576

/* if the output buffer reaches this limit, it gets flushed. This means,
 * that 0.5MB input data may produce max 1MB data in output buffer, otherwise
 * a buffer overflow may occur, and data does not get processed correctly.
 * However, every Process_vx function checks buffer boundaries.
 */
#define OUTPUT_FLUSH_LIMIT BUFFSIZE * 0.8


/* prototypes */

int InitSymbols(void);

void Setv6Mode(int mode);

int Getv6Mode(void);

int Proto_num(char *protostr);

void format_file_block_header(void *header, char **s, int tag);

char *format_csv_header(void);

char *get_record_header(void);

void set_record_header(void);

void format_file_block_record(void *record, char **s, int tag);

void flow_record_to_pipe(void *record, char ** s, int tag);

void flow_record_to_csv(void *record, char ** s, int tag);

int ParseOutputFormat(char *format, int plain_numbers);

void format_special(void *record, char ** s, int tag);


uint32_t Get_fwd_status_id(char *status);

char *Get_fwd_status_name(uint32_t id);

#define FIXED_WIDTH 1
#define VAR_LENGTH  0

#ifdef __SUNPRO_C
extern 
#endif
inline void Proto_string(uint8_t protonum, char *protostr);

#ifdef __SUNPRO_C
extern 
#endif
inline void format_number(uint64_t num, char *s, int fixed_width);

#ifdef __SUNPRO_C
extern 
#endif
inline void condense_v6(char *s);

#define TAG_CHAR ''

#endif //_NF_COMMON_H


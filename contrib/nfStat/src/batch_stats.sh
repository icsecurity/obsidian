#!/bin/bash

function istogrammi 
{
## VALUTAZIONI HISTOGRAMMI IP SU "MOMENTI ANOMALI" DEI GRAFICI

# array giorno "anno mese giorno ora minuto secondo"
# giorno[1]="2010 09 29 "

#### STREAMING ###
# entropia
giorno[0]="2010 09 29 01 24"
option[0]="-H 2"
fname[0]="str1-M24"
giorno[1]="2010 09 29 03 24"
option[1]="-H 2"
fname[1]="str2-M24"
giorno[2]="2011 02 13 01 27 54"
option[2]="-H 2"
fname[2]="ddos1-2"
giorno[3]="2011 02 13 01 31 54"
option[3]="-H 2"
fname[3]="ddos2-3"
giorno[4]="2011 02 13 06 47 54"
option[4]="-H 2"
fname[4]="ddos3-4"
giorno[5]="2011 02 13 04 06 54"
option[5]="-H 2"
fname[5]="ddos4-5"
giorno[6]="2011 02 13 07 24 54"
option[6]="-H 2"
fname[6]="ddos5-6"
giorno[7]="2011 02 13 06 47 54"
option[7]="-H 1"
fname[7]="ddos6-7"
giorno[8]="2010 09 29 01 24"
option[8]="-H 2"
fname[8]="str1-8"

####### MINUTI PRECEDENTE ########
giorno[9]="2010 09 29 01 23"
option[9]="-H 2"
fname[9]="str1-M23"
giorno[10]="2010 09 29 03 23"
option[10]="-H 2"
fname[10]="str2-10"
giorno[11]="2011 02 13 01 27 53"
option[11]="-H 2"
fname[11]="ddos1-11"
giorno[12]="2010 09 29 01 23"
option[12]="-H 2"
fname[12]="str1-12"
giorno[13]="2011 02 13 01 31 53"
option[13]="-H 2"
fname[13]="ddos2-13"
giorno[14]="2011 02 13 06 47 53"
option[14]="-H 2"
fname[14]="ddos3-14"
giorno[15]="2011 02 13 04 06 53"
option[15]="-H 2"
fname[15]="ddos4-15"
giorno[16]="2011 02 13 07 24 53"
option[16]="-H 2"
fname[16]="ddos5-16"
giorno[17]="2011 02 13 06 47 53"
option[17]="-H 1"
fname[17]="ddos6-17"

####### MINUTI SUCCESSO ########
giorno[18]="2010 09 29 01 25"
option[18]="-H 2"
fname[18]="str1-M25"
giorno[19]="2010 09 29 03 25"
option[19]="-H 2"
fname[19]="str2-19"
giorno[20]="2011 02 13 01 27 55"
option[20]="-H 2"
fname[20]="ddos1-20"
giorno[21]="2010 09 29 01 25"
option[21]="-H 2"
fname[21]="str1-21"
giorno[22]="2011 02 13 01 31 55"
option[22]="-H 2"
fname[22]="ddos2-22"
giorno[23]="2011 02 13 06 47 55"
option[23]="-H 2"
fname[23]="ddos3-23"
giorno[24]="2011 02 13 04 06 55"
option[24]="-H 2"
fname[24]="ddos4-24"
giorno[25]="2011 02 13 07 24 55"
option[25]="-H 2"
fname[25]="ddos5-25"
giorno[26]="2011 02 13 06 47 55"
option[26]="-H 1"
fname[26]="ddos6-26"



element_count=${#giorno[@]}
index=1

while [ "$index" -lt "$element_count" ]
do    
  echo "[INDEX $index] Analizzo calcoli giorno ${giorno[$index]}"
  anno=$(echo ${giorno[$index]} | awk '{print $1}')
  mese=$(echo ${giorno[$index]} | awk '{print $2}')
  giorno=$(echo ${giorno[$index]} | awk '{print $3}')
  ora=$(echo ${giorno[$index]} | awk '{print $4}')
  minuti=$(echo ${giorno[$index]} | awk '{print $5}')
  opt=${option[$index]}
  echo "minuti $minuti"

  # cmd="./nfStat -R /mnt/nfsen/extrabirewp2000/$anno/$mese/$giorno/ $opt -O ./resultsistogrammi/${anno}_${mese}_${giorno}_${misura}"
  cmd="./nfStat -R /mnt/nfsen/extrabirewp2000/$anno/$mese/$giorno/ $opt \
	-s ${anno}-${mese}-${giorno}\ ${ora}:${minuti} -d 1 -O ./rs/${anno}_${mese}_${giorno}_${ora}_${minuti}_${fname[$index]}"

  echo "Eseguo comando "
  echo "$cmd"
  $cmd  
  let "index = $index + 1"
done

# svn add rs
# svn add rs/* 
# svn ci 

exit 0

}

#29/09/2010
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -k 0 -O ./results/out_2010_09_29_srcip
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -b 300 -k 2 -O ./results/out_2010_09_29_dstip
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -k 2 -O ./results/out_2010_09_29_srcip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -k 3 -O ./results/out_2010_09_29_dstip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -B 0 -O ./results/out_2010_09_29_flows-bytes-pckts

#for i in `seq 2 10`; do
#	./nfStat -R /mnt/nfsen/extrabirewp2000/2010/09/29/ -Y 2 -a $i -O ./results/out_2010_09_29_alpha_$i
#done

#06/10/2010
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/10/06/ -B 0 -O ./results/out_2010_10_06_flows-bytes-pckts -b 300

#14/12/2010
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -k 0 -O ./results/out_2010_12_14_srcip
./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -K 2 -O ./results/2010_12_14_dstip > ./results/2010_12_14_dstip_details
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -k 2 -O ./results/out_2010_12_14_srcip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -k 3 -O ./results/out_2010_12_14_dstip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -B 0 -O ./results/out_2010_12_14_flows-bytes-pckts -b 300

# for i in `seq 2 10`; do
#        ./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/14/ -Y 2 -a $i -O ./results/out_2010_12_14_alpha_$i
# done

#21/12/2010
#./nfStat -R /mnt/nfsen/extrabirewp2000/2010/12/21/ -B 0 -O ./results/out_2010_12_21_flows-bytes-pckts -b 300

#06/02/2011
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/06/ -k 0 -O ./results/out_2011_02_06_srcip
./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/06/ -K 2 -O ./results/2011_02_06_dstip > ./results/2011_02_06_dstip_details
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/06/ -k 2 -O ./results/out_2011_02_06_srcip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/06/ -k 3 -O ./results/out_2011_02_06_dstip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/06/ -B 0 -O ./results/out_2011_02_06_flows-bytes-pckts -b 300

#13/02/2011
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/13/ -k 0 -O ./results/out_2011_02_13_srcip
./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/13/ -K 2 -O ./results/2011_02_13_dstip > ./results/2011_02_13_dstip_details
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/13/ -k 2 -O ./results/out_2011_02_13_srcip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/13/ -k 3 -O ./results/out_2011_02_13_dstip-port
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/13/ -B 0 -O ./results/out_2011_02_13_flows-bytes-pckts -b 300

#20/02/2011
#./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/20/ -B 0 -O ./results/out_2011_02_20_flows-bytes-pckts -b 300
# for i in `seq 2 10`; do
#         ./nfStat -R /mnt/nfsen/extrabirewp2000/2011/02/20/ -Y 2 -a $i -O ./results/out_2011_02_20_alpha_$i
# done

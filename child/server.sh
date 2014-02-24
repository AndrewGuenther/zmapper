#!/bin/bash

RUN_NUM=0
SCAN_ACTIVE=0

function launch_zmap {
   let "RUN_NUM += 1"
   zmap -p $1 -i eth0 -d -o /tmp/zmap-results-$RUN_NUM 2> /tmp/zmap-err-$RUN_NUM > /dev/null &
   SCAN_ACTIVE=$!
}

function parse_command {
   while read data; do
      op=$(echo $data | cut -f 1 -d " ")

      case "$op" in
         start)
            echo $(echo $data | cut -f 1 -d " " --complement)
            if [ $SCAN_ACTIVE -eq 0 ]; then
               launch_zmap $(echo $data | cut -f 1 -d " " --complement)
            fi
            ;;
         stop)
            if [ $SCAN_ACTIVE -ne 0 ]; then
               kill $SCAN_ACTIVE
               SCAN_ACTIVE=0
            fi
            ;;
         report)
            echo $(tail -n 1 /tmp/zmap-err-$RUN_NUM)
            ;;
      esac
   done
}

rm report_pipe 2> /dev/null
mkfifo report_pipe
nc -klp 9876 < report_pipe | parse_command > report_pipe

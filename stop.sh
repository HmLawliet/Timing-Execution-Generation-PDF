#!/bin/bash 

if [[ `ps -ef | grep celery | grep -v grep | wc -l ` > 0  ]];then 
	ps -ef | grep celery | grep -v grep | awk '{print $2}' | xargs kill -15
fi 


if [[ `ps -ef | grep defunct | grep -v grep | wc -l ` > 0  ]];then 
	ps -ef | grep defunct | grep -v grep | awk '{print $2}' | xargs kill -15
fi  

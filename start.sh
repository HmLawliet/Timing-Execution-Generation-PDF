#!/bin/bash 

setsid python celeryapp.py >/dev/null 2>&1 & 

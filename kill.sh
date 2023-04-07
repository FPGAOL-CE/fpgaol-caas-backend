#!/bin/bash
ps -eLF | grep 'python server.py' | grep -v grep | awk '{print $2}' | xargs kill

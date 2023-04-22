#!/bin/bash -e
mkdir -p jobs
setsid python server.py &

#!/usr/bin/env bash

echo
echo "===== SYSTEM STATUS ====="
echo

echo "Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}"

echo
echo "Disk:"
df -h /

echo
echo "Memory:"
free -h

echo
echo "Load:"
uptime

echo
echo "Recent errors:"
docker ps -a --filter status=exited

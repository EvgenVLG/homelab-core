#!/usr/bin/env bash
set -e

ACTION=$1
SERVICE=$2

SERVICES=(
  adguard
  caddy
  homepage
  portainer
  n8n
  homeassistant
)

if [[ ! " ${SERVICES[@]} " =~ " ${SERVICE} " ]]; then
  echo "Service not allowed"
  exit 1
fi

case "$ACTION" in
  start)
    docker start $SERVICE
    ;;
  stop)
    docker stop $SERVICE
    ;;
  restart)
    docker restart $SERVICE
    ;;
  logs)
    docker logs --tail 50 $SERVICE
    ;;
  status)
    docker ps --filter name=$SERVICE
    ;;
  *)
    echo "Usage:"
    echo "docker-service.sh [start|stop|restart|logs|status] service"
    ;;
esac

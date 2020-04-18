PROMETHEUS_PORT=9090
CONTAINER_NAME=prometheus

docker container inspect $CONTAINER_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Docker instances ($CONTAINER_NAME) exist. Trying to stop and delete it...\n"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

printf "Starting a new ($CONTAINER_NAME) container...\n"
docker run -d \
  --name $CONTAINER_NAME \
  -p $PROMETHEUS_PORT:9090 \
  -v $PWD/../ansible/artifacts/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus:v2.14.0

IP_ADDRESS=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME})
echo "${CONTAINER_NAME} is running "
echo "${CONTAINER_NAME} ip address is: ${IP_ADDRESS}"
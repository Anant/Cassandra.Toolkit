GRAFANA_PORT=3000
CONTAINER_NAME=grafana

GF_AUTH_BASIC_ENABLED=true
GF_AUTH_ANONYMOUS_ENABLED=false
GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
GF_SECURITY_ADMIN_PASSWORD=admin
GF_PANELS_DISABLE_SANITIZE_HTML=true

docker container inspect $CONTAINER_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Docker instances ($CONTAINER_NAME) exist. Trying to stop and delete it...\n"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

printf "Starting a new ($CONTAINER_NAME) container...\n"
docker run -d \
     -v $PWD/artifacts/grafana/dashboards:/etc/grafana/provisioning/dashboards:z \
     -v $PWD/artifacts/grafana/datasources:/etc/grafana/provisioning/datasources:z \
     -e "GF_AUTH_BASIC_ENABLED=$GF_AUTH_BASIC_ENABLED" \
     -e "GF_AUTH_ANONYMOUS_ENABLED=$GF_AUTH_ANONYMOUS_ENABLED" \
     -e "GF_SECURITY_ADMIN_PASSWORD=$GF_SECURITY_ADMIN_PASSWORD" \
     -e "GF_AUTH_ANONYMOUS_ORG_ROLE=$GF_AUTH_ANONYMOUS_ORG_ROLE" \
     -e "GF_PANELS_DISABLE_SANITIZE_HTML=$GF_PANELS_DISABLE_SANITIZE_HTML" \
    --name $CONTAINER_NAME \
    --publish $GRAFANA_PORT:3000 \
    grafana/grafana:6.5.1

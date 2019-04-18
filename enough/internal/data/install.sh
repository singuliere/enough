    docker run --rm \
       -ti \
       -v $HOME/.enough:/root/.enough \
       -v /etc/ssl/certs:/etc/ssl/certs:ro \
       -v /usr/local/share/ca-certificates:/usr/local/share/ca-certificates:ro \
       -v /var/run/docker.sock:/var/run/docker.sock \
       --entrypoint enough \
       enough{{ this.version }} "$@"

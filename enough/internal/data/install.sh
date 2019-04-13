    docker run --rm \
       -ti \
       -v $HOME/.enough:/root/.enough \
       -v /var/run/docker.sock:/var/run/docker.sock \
       --entrypoint enough \
       enough%version% "$@"

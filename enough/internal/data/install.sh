#!/bin/bash

function enough() {
    docker run --rm -ti \
       -v $HOME/.enough:/opt/.enough \
       -v /var/run/docker.sock:/var/run/docker.sock \
       enough:%version% "$@"
}

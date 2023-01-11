#!/bin/bash

docker run \
    --env-file=.env \
    --network="host" \
    -v /home/colet/programming/projects/crawler_docker/logs:/app/logs \ 
    crawler_image
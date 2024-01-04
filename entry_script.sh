#!/bin/bash

# mount storage
sudo blobfuse /home/vscodeuser/workspace --tmp-path=/mnt/resource/blobfusetmp  --config-file=/fuse_connection.cfg -o allow_other

# start code server
code tunnel user login --provider github --access-token ${GITHUB_ACCESS_TOKEN}
code tunnel --accept-server-license-terms

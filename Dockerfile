FROM ubuntu:latest

# Storage mount parameters
ARG STORAGE_ACCOUNT_NAME
ENV STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME
ARG STORAGE_CONTAINER_NAME
ENV STORAGE_CONTAINER_NAME=$STORAGE_CONTAINER_NAME
ARG STORAGE_ACCOUNT_KEY
ENV STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY

# install vscode
RUN apt update && apt install curl gpg sudo -y
RUN curl -sL https://go.microsoft.com/fwlink/?LinkID=760868 > code.deb
RUN apt install ./code.deb -y

# install blobfuse for persistent storage
RUN curl -sL -O https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN rm -r packages-microsoft-prod.deb
RUN apt-get install blobfuse libcurl4-gnutls-dev -y 

# https://medium.com/srcecde/mount-azure-blob-storage-as-file-system-on-docker-container-8e44f315b526
RUN echo "accountName ${STORAGE_ACCOUNT_NAME}" > /fuse_connection.cfg
RUN echo "accountKey ${STORAGE_ACCOUNT_KEY}" >> /fuse_connection.cfg
RUN echo "containerName ${STORAGE_CONTAINER_NAME}" >> /fuse_connection.cfg

RUN mkdir -p /mnt/resource/blobfusetmp

COPY ./entry_script.sh .
RUN chmod +x ./entry_script.sh

# create non sudo user and add to sudo group
RUN useradd -m -p '' -s /bin/bash vscodeuser
RUN usermod -aG sudo vscodeuser

# make default user
USER vscodeuser
WORKDIR /home/vscodeuser
RUN mkdir -p /home/vscodeuser/workspace

ENV DONT_PROMPT_WSL_INSTALL true

ENTRYPOINT ["/entry_script.sh"]
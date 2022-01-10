#!/bin/bash

DOCKER='docker' # Change to podman if you want to use podman
DOCKER_IMAGE='clearpass:dev'
SUDO=

SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

build_image() {
    echo "Building image $DOCKER_IMAGE"
    pushd "$SCRIPT_DIR" >/dev/null || exit 1

    if ! $SUDO docker build --pull -t "$DOCKER_IMAGE" .; then
        echo 'Build failed.  Exiting!'
        exit 2
    fi

    popd >/dev/null || exit 1
}

if [ "$TERM" != 'dumb' ] ; then
    TTY='-it'
fi

if [ "$( uname -s )" != 'Darwin' ]; then
    if [ ${DOCKER} = 'docker' ]; then
        if [ ! -w "$DOCKER_SOCKET" ]; then
            SUDO='sudo'
        fi
    fi
fi

REBUILD=
while getopts "r" OPTION; do
    case $OPTION in
        r)
            REBUILD='yes'
            shift
            ;;
        \?)
            echo 'Invalid argument.'
            exit 1
            ;;
    esac
done

if [ -n "$REBUILD" ]; then
    build_image
else
    if ! $SUDO $DOCKER image ls | awk '{print $1":"$2}' | grep -q "^$DOCKER_IMAGE"; then
        build_image
    fi
fi

$SUDO $DOCKER run $TTY --rm -v "$SCRIPT_DIR":/usr/src "$DOCKER_IMAGE" "$@"

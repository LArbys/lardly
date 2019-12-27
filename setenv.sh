#!/bin/bash

__where__="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export LARDLY_BASEDIR=${__where__}

[[ ":$PYTHONPATH:" != *":${LARDLY_BASEDIR}/lardly:"* ]] && \
    export PYTHONPATH="${LARDLY_BASEDIR}:${PYTHONPATH}"

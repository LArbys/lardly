#!/bin/bash

__where__="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export LARDLY_BASEDIR=${__where__}
export LARDLY_BINDIR=${LARDLY_BASEDIR}

[[ ":$PYTHONPATH:" != *":${LARDLY_BASEDIR}/lardly:"* ]] && \
    export PYTHONPATH="${LARDLY_BASEDIR}:${PYTHONPATH}"
[[ ":$PATH:" != *":${LARDLY_BINDIR}:"* ]] && \
    export PATH="${LARDLY_BINDIR}:${PATH}"



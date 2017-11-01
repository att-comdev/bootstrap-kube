#!/bin/bash
# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


set -eux

HELM=${1}
HELM_PIDFILE=${2}
SERVE_DIR=${3}

${HELM} init --client-only

if [[ -s ${HELM_PIDFILE} ]]; then
    HELM_PID=$(cat "${HELM_PIDFILE}")
    if ps "${HELM_PID}"; then
        kill "${HELM_PID}"
        sleep 0.5
        if ps "${HELM_PID}"; then
            echo Failed to terminate Helm, PID = "${HELM_PID}"
            exit 1
        fi
    fi
fi

${HELM} serve & > /dev/null
HELM_PID=${!}
echo Started Helm, PID = "${HELM_PID}"
echo "${HELM_PID}" > "${HELM_PIDFILE}"

set +x
if [[ -z $(curl -s 127.0.0.1:8879 | grep 'Helm Repository') ]]; then
    while [[ -z $(curl -s 127.0.0.1:8879 | grep 'Helm Repository') ]]; do
       sleep 1
       echo "Waiting for Helm Repository"
    done
else
    echo "Helm serve already running"
fi
set -x

if ${HELM} repo list | grep -q "^stable" ; then
    ${HELM} repo remove stable
fi

${HELM} repo add local http://localhost:8879/charts

mkdir -p "${SERVE_DIR}"
cd "${SERVE_DIR}"
git clone --depth 1 https://git.openstack.org/openstack/openstack-helm-infra.git || true
cd openstack-helm-infra

make helm-toolkit

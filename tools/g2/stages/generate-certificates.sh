#!/usr/bin/env bash

set -e

source "${GATE_UTILS}"

OUTPUT_DIR="${TEMP_DIR}/config"
mkdir -p "${OUTPUT_DIR}"
chmod 777 "${OUTPUT_DIR}"
OUTPUT_FILE="${OUTPUT_DIR}/combined.yaml"

for source_dir in $(config_configuration); do
    log Copying configuration from "${source_dir}"
    cat "${WORKSPACE}/${source_dir}"/*.yaml >> "${OUTPUT_FILE}"
done

log "Setting up local caches.."
nginx_cache_and_replace_tar_urls "${OUTPUT_DIR}"/*.yaml
registry_replace_references "${OUTPUT_DIR}"/*.yaml

FILES=($(ls "${OUTPUT_DIR}"))

log Generating certificates
docker run --rm -t \
    -w /target \
    -v "${OUTPUT_DIR}:/target" \
    -e "PROMENADE_DEBUG=${PROMENADE_DEBUG}" \
    "${IMAGE_PROMENADE}" \
        promenade \
            generate-certs \
                -o /target \
                "${FILES[@]}"

#!/usr/bin/env bash

CLOUD_PROVIDER=""
REGION=""

function get_metadata() {

  # AWS
  METADATA=$(curl --fail http://169.254.169.254/latest/meta-data/placement/availability-zone)
  if [ "${?}" == '0' ]; then
    CLOUD_PROVIDER="AWS"
    REGION="${METADATA%-*}"
    return 0
  fi

  # GCP
  METADATA=$(curl --fail http://169.254.169.254/computeMetadata/v1/instance/zone -H "Metadata-Flavor: Google")
  if [ "${?}" == '0' ]; then
    CLOUD_PROVIDER="GCP"
    METADATA="${METADATA##*/}"
    REGION="${METADATA%-*}"
    return 0
  fi

  # Azure
}

get_metadata
echo "Using Cloud Provider: ${CLOUD_PROVIDER}, Region: ${REGION}"

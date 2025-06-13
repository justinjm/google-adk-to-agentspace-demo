#!/bin/bash

# Source the environment variables
if [ -f .env-registration ]; then
  echo "Loading environment variables from .env-registration"
  set -a # automatically export all variables
  source .env-registration
  set +a
else
  echo "Error: .env-registration file not found."
  exit 1
fi

curl -X DELETE \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/authorizations/${AUTH_ID}"
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

# Execute the curl command
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/authorizations?authorizationId=${AUTH_ID}" \
    -d "{
          \"name\": \"projects/${PROJECT_ID}/locations/global/authorizations/${AUTH_ID}\",
          \"serverSideOauth2\": {
            \"clientId\": \"${CLIENT_ID}\",
            \"clientSecret\": \"${CLIENT_SECRET}\",
            \"authorizationUri\": \"${AUTH_URI}\",
            \"tokenUri\": \"${TOKEN_URI}\"
          }
        }"

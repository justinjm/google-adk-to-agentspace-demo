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
    "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
    -d "{
          \"displayName\": \"Data Science Agent\",
          \"description\": \"A multi-agent system designed for sophisticated data analysis \",
          \"adk_agent_definition\": {
            \"tool_settings\": {
              \"tool_description\": \"Mulitple data science related tools\"
            },
            \"provisioned_reasoning_engine\": {
              \"reasoning_engine\": \"projects/${PROJECT_ID}/locations/global/reasoningEngines/${RESOURCE_ID}\"
            },
            \"authorizations\": [\"projects/${PROJECT_ID}/locations/global/authorizations/${AUTH_ID}\"]
          }
        }"

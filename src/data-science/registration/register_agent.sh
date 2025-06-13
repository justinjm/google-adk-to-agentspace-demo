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

# ==============================================================================
# JSON Payload
#
# This section constructs the JSON data that will be sent in the API request.
# It uses the environment variables defined above.
# ==============================================================================

# The -d '{}' part of a curl command is the "data" or payload. Storing it in a 
# variable makes the command easier to read and debug.
JSON_PAYLOAD=$(cat <<EOF
{
  "displayName": "${DISPLAY_NAME}",
  "description": "${DESCRIPTION}",
  "adk_agent_definition": {
    "tool_settings": {
      "tool_description": "${TOOL_DESCRIPTION}"
    },
    "provisioned_reasoning_engine": {
      "reasoning_engine": "projects/${PROJECT_ID}/locations/global/reasoningEngines/${ADK_DEPLOYMENT_ID}"
    },
    "authorizations": [
      "projects/${PROJECT_ID}/locations/global/authorizations/${AUTH_ID}"
    ]
  }
}
EOF
)

# ==============================================================================
# cURL Command Execution
#
# This section executes the API call to create the agent.
# It authenticates using your gcloud credentials.
# ==============================================================================

echo "Sending request to create agent..."

# The curl command sends the actual request.
# -X POST: Specifies this is a POST request, used for creating new resources.
# -H: Sets the necessary headers for authorization, content type, and project ID.
# -d: Sends the JSON_PAYLOAD variable as the request body.
# The URL is now correctly formatted on a single line.
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
  -d "${JSON_PAYLOAD}"

echo -e "\n\nScript execution finished."
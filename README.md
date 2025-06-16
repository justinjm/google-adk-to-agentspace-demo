# Google ADK to Agentspace Demo Deployment

Create an Agent with Google ADK (Agent Development Kit), deploy to Agent Engine API and then register for use in Agentspace.

This repository uses an example Data Science agent found [here](https://github.com/google/adk-samples/tree/main/python/agents/data-science).

See more details on [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) and [ADK](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart)

## Pre-requisites

Assumes the following is setup: 

1. Google Cloud project with billing enabled
2. An [Agentspace Enterprise Plus ](https://cloud.google.com/agentspace/agentspace-enterprise/docs/overview) app

## Data Science Agent - Workflow steps

### Workflow summary

1. setup GCP and local environment
2. Create agent and test locally
3. deploy agent to vertex ai ai agent engine
4. register agent in agentspace

### Setup and run agent locally

#### install poetry

Navigate to the `src/data-science/` directory first and then run `poetry install` to install dependencies for a local virtual environment.

[https://python-poetry.org/docs/#installing-with-the-official-installer](https://python-poetry.org/docs/#installing-with-the-official-installer)  

```sh
cd src/data-science && poetry install
```

Then activate the virual environment

```sh
source $(poetry env info --path)/bin/activate
```

### test agent locally

1. copy `src/data-science/.env-example` to `src/data-science/.env` and update per instructions in the comments

2. create BQ table

```bash
python3 data_science/utils/create_bq_table.py
```

3. Setup BQML as a RAG corpus:

```bash
python3 data_science/utils/reference_guide_RAG.py
```

4. Run agent locally via web

```sh
poetry run adk web
```

See [src/data-science/README.md](src/data-science/README.md) for more details.

### Deploy to vertex ai agent engine

Set environment variables for deployment from terminal

```sh
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
export LOCATION="us-central1"
export APP_ID="enterprise-search-17417040_1741704019737" # ID of agentspace app 
```

#### Set up your service agent permissions

https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/set-up#service-agent

##### manually generate service agent (if needed)

```sh
gcloud beta services identity create --service=aiplatform.googleapis.com --project=${PROJECT_ID}
```

##### Add BigQuery and Vertex AI roles to Agent Engine service agent

```sh
export RE_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.user"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.dataViewer"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/aiplatform.user"
```

#### Build and deploy agent to agent engine

Next, you need to create a `.whl` file for your agent. From the `data-science` directory, run this command:

```sh
poetry build --format=wheel --output=deployment
```

This will create a file named `data_science-0.1-py3-none-any.whl` in the `deployment` directory.

Then run the below command. This will create a staging bucket in your GCP project and deploy the agent to Vertex AI Agent Engine:

```sh
cd deployment/ && python3 deploy.py --create
```

When this command returns, if it succeeds it will print an AgentEngine resource name that looks something like this:

```sh
...
Successfully created agent: projects/746038361521/locations/us-central1/reasoningEngines/2513685891235446784
```

The last sequence of digits is the AgentEngine resource ID.

Once you have successfully deployed your agent, you can interact with it using the `test_deployment.py` script in the `deployment` directory. Store the agent's resource ID in an environment variable and run the following command:

```sh 
export RESOURCE_ID=2513685891235446784
export USER_ID="user1"
python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

### Register Agent in Agentspace

#### Setup OAuth2  and Client ID

* Obtain a OAuth2 client ID / secret
  * Console -> [OAuth](https://console.cloud.google.com/auth/overview) -> Clients --> Create client ID
    * Application type: `Web Application`
    * Name: `Agentspace` (or whatever you wish)
    * Authorized redirect URIs: add redirect url `https://vertexaisearch.cloud.google.com/oauth-redirect`
  * Click create then download JSON or copy/paste the values
    * Client ID
    * Client secret
    * Auth URI
    * Token URI

#### Configure environment variables

For easier running of the following curl commands

* Copy `.env-registration-example` to `.env-registration` , update per instructions in the comments and then save
* navigate to the registration directory and load the environment variables:

```bash
cd ../registration/ && source .env-registration
```

#### Add authorization to agentspace

First we add the authorization to agentspace:

```sh
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
```

#### enable APIs and user permissions

First setup the following if not already:

1. Enable the DiscoveryEngine API for the GCP project.

```sh
gcloud services enable discoveryengine.googleapis.com
```

2. Enable the Vertex AI user and Vertex AI viewer role in your discoveryengine service account. This is required for Agentspace to call your ADK agent. Go to IAM in cloud console, search for discoveryengine and add permissions to that Service Account. To see the discoveryengine service account you need to check the "Include Google-provided role grants" on the IAM console screen.

```bash
export DISCOVERYENGINE_SA_EMAIL="service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com"
# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${DISCOVERYENGINE_SA_EMAIL}" \
    --role="roles/aiplatform.user" \
    --condition=None

## Grant Vertex AI viewer role 
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${DISCOVERYENGINE_SA_EMAIL}" \
    --role="roles/aiplatform.viewer" \
    --condition=None
```

```bash
export CC_SA_EMAIL="service-${PROJECT_NUMBER}gcp-sa-aiplatform-cc.iam.gserviceaccount.com"
# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${DISCOVERYENGINE_SA_EMAIL}" \
    --role="roles/aiplatform.user" \
    --condition=None

## Grant Vertex AI viewer role 
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:${DISCOVERYENGINE_SA_EMAIL}" \
    --role="roles/aiplatform.viewer" \
    --condition=None
```

#### register agent with agentspace

Lastly, we register the agent with agentspace by running:

```bash
curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: ${PROJECT_ID}" \
"https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
-d "{
    \"displayName\": \"${DISPLAY_NAME}\",
    \"description\": \"${DESCRIPTION}\",
    \"adk_agent_definition\": {
        \"tool_settings\": {
            \"tool_description\": \"${TOOL_DESCRIPTION}\"
        },
        \"provisioned_reasoning_engine\": {
            \"reasoning_engine\": \"projects/${PROJECT_ID}/locations/global/reasoningEngines/${ADK_DEPLOYMENT_ID}\"
        },
        \"authorizations\": [
            \"projects/${PROJECT_NUMBER}/locations/global/authorizations/${AUTH_ID}\"
        ]
    }
}"
```


Now the agent should be ready to use in Agentspace.

![](/img/agentspace-adk-agent.png)



#### View agent

```bash
export AGENT_RESOURCE_NAME="projects/746038361521/locations/global/collections/default_collection/engines/enterprise-search-17417040_1741704019737/assistants/default_assistant/agents/xxxxxsdafasdfasdfasdf"
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/${AGENT_RESOURCE_NAME}"
```



### CLEANUP

TODO - finish


#### List all authorizations 

```sh
curl -X GET \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/authorizations"
```

#### Delete a single authorization 


```bash
curl -X DELETE \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ${PROJECT_ID}" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/authorizations/${AUTH_ID}"
```

#### View all agents registered in agentspace

```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
```

#### Delete agent from Agentspace

```bash
export AGENT_RESOURCE_NAME="projects/746038361521/locations/global/collections/default_collection/engines/enterprise-search-17417040_1741704019737/assistants/default_assistant/agents/13486992500677800922"
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/${AGENT_RESOURCE_NAME}"
```

#### Delete agent from Agent Engine

1. Delete deployed agent

```sh
## WARNING! will delete deployed agent
#python3 deployment/deploy.py --delete --resource_id=RESOURCE_ID
```

2. Delete BQ dataset / table
3. Delete GCS bucket


## References

* [VeerMuchandi/corporate\_analyst](https://github.com/VeerMuchandi/corporate_analyst) - example corporate analyst agent
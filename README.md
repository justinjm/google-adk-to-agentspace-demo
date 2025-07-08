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
    --role="roles/bigquery.admin"
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

Now, navigate to the deployment directory: 

```sh
cd deployment/ 
```

Then run the below command to create a staging bucket in your GCP project and deploy the agent to Vertex AI Agent Engine:

```sh
poetry run python deploy.py --create
```

First, it will try to create a code extension and should return the folloiwng message:

```sh
Extension created. Resource name: projects/746038361521/locations/us-central1/extensions/3783677896409743360
```

you can save this value to the `.env` file so a new one wont be created next time.

When this command completes, if it succeeds it will print an AgentEngine resource name that looks something like this:

```sh
Successfully created agent: projects/746038361521/locations/us-central1/reasoningEngines/1184473090277507072
```

The last sequence of digits is the AgentEngine resource ID.

Once you have successfully deployed your agent, you can interact with it using the `test_deployment.py` script in the `deployment` directory. Store the agent's resource ID in an environment variable and run the following command:

```sh 
export RESOURCE_ID=1184473090277507072
export USER_ID="user1"
poetry run python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

### Register Agent in Agentspace


#### Configure environment variables

For easier running of the following curl commands

* Copy `.env-registration-example` to `.env-registration` , update per instructions in the comments and then save
* navigate to the registration directory and load the environment variables:

```bash
cd ../registration/ && source .env-registration
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

#### register agent with agentspace

Lastly, we register the agent with agentspace by running the below.

Note we set the `ADK_DEPLOYMENT_ID` here to be sure it's correct and so we do not have to check/reload the `.env-registration` file again

```bash
export ADK_DEPLOYMENT_ID=$RESOURCE_ID

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
        }
    }
}"
```

Now the agent should be ready to use in Agentspace.

![](/img/agentspace-adk-agent.png)

#### View agent

```bash
export AGENT_RESOURCE_ID=17434484936421622698
export AGENT_RESOURCE_NAME="projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents/${AGENT_RESOURCE_ID}"
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/${AGENT_RESOURCE_NAME}"
```

### CLEANUP

#### View all agents registered in agentspace

```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
```

#### Delete agent from Agentspace

Update the `AGENT_RESOURCE_ID` with the value from running command above to list all agents OR from the response message (`name`) after registring the agent.

```bash
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/${AGENT_RESOURCE_NAME}"
```

#### Delete deployed agent in Agent Engine

```sh
## WARNING! will delete deployed agent
#poetry run python deployment/deploy.py --delete --resource_id=$RESOURCE_ID
```

#### Delete vertex ai extension(s) - included scripts delete all or selected

```sh
poetry run python delete_extensions.py --mode delete_all --project_id $PROJECT_ID
poetry run python delete_extensions.py --mode delete_list --ids 6738311930848477184 1334788424422391808 --project_id $PROJECT_ID
```

#### Delete BQ dataset / table

https://cloud.google.com/bigquery/docs/managing-datasets#delete-datasets

```sh
# bq rm -r -f -d ${PROJECT_ID}:forecasting_sticker_sales
```

#### Delete GCS bucket

https://cloud.google.com/storage/docs/deleting-buckets

```sh

# gcloud storage rm --recursive gs://${PROJECT_ID}-adk-staging
```


## References

* [VeerMuchandi/corporate\_analyst](https://github.com/VeerMuchandi/corporate_analyst) - example corporate analyst agent
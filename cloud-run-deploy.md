# Deploying to Cloud Run

TODO - finish and test these steps

* [Host AI apps and agents on Cloud Run  |  Cloud Run Documentation  |  Google Cloud](https://cloud.google.com/run/docs/ai-agents)
* [Cloud Run - Agent Development Kit](https://google.github.io/adk-docs/deploy/cloud-run/#code-files)


## Workflow Steps 

With these files in `src/data-science/`, you can build and deploy your agent to Cloud Run. This process replaces the Agent Engine deployment flow (i.e., you won't use the `deployment/deploy.py` script).

1.  **Build the container image using Cloud Build:** Make sure you are in the root of your project directory.
    
    ```bash
    export PROJECT_ID=$(gcloud config get-value project)

    gcloud builds submit src/data-science --tag "gcr.io/${PROJECT_ID}/data-science-agent"
    ```
2.  **Deploy to Cloud Run:** When you deploy, you must provide the necessary environment variables that your agent needs to connect to BigQuery and other services.
    
    ```bash
    # Get all the environment variables from your .env file 
    # Ensure you have a .env file inside src/data-science/ 
    ENV_VARS=$(sed 's/^#.*//' src/data-science/.env | sed 's/^export //g' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')  
    
    gcloud run deploy data-science-agent \
        --image="gcr.io/${PROJECT_ID}/data-science-agent" \
        --platform=managed \
        --region=us-central1 \
        --allow-unauthenticated \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},${ENV_VARS}"
    ```
    
    **Note:** You'll need to configure the environment variables (`--set-env-vars`) your agent requires, such as `BQ_DATA_PROJECT_ID`, `BQ_DATASET_ID`, model names, etc., as defined in your `.env` file and `README.md`. The command above attempts to load them from your `.env` file, but you can also set them manually.
    
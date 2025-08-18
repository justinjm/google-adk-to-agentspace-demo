# Copyright 2025 Google LLC
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

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""
import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.adk.agents.callback_context import CallbackContext


from data_science.sub_agents.bqml.tools import (
    check_bq_models,
    rag_response,
)
from .prompts import return_instructions_bqml


from data_science.sub_agents.bigquery.agent import database_agent as bq_db_agent
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)


# BigQuery built-in tools in ADK
# https://google.github.io/adk-docs/tools/built-in-tools/#bigquery
ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_schema_and_samples"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_bqml()
            + f"""

   </BQML Reference for this query>
    
    <The BigQuery schema of the relevant data with a few sample rows>
    {schema}
    </The BigQuery schema of the relevant data with a few sample rows>
    """
        )


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )
    database_agent = (
        bq_db_agent
        if tool_context.state["all_db_settings"]["use_database"] == "BigQuery"
        # else pg_db_agent
        else None
    )
    agent_tool = AgentTool(agent=database_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output

bigquery_tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.ALLOWED, # to be able to execute CREATE MODEL statement
    max_query_result_rows=80
)
bq_execute_sql = BigQueryToolset(
    tool_filter=bigquery_tool_filter,
    bigquery_tool_config=bigquery_tool_config
)

root_agent = Agent(
    model=os.getenv("BQML_AGENT_MODEL"),
    name="bq_ml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[bq_execute_sql, check_bq_models, call_db_agent, rag_response],
)

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

"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the bigquery agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

import os
from data_science.utils.utils import get_env_var


def return_instructions_bigquery() -> str:

    NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")
    if NL2SQL_METHOD == "BASELINE" or NL2SQL_METHOD == "CHASE":
        db_tool_name = "initial_bq_nl2sql"
    else:
        db_tool_name = None
        raise ValueError(f"Unknown NL2SQL method: {NL2SQL_METHOD}")

    instruction_prompt_bigquery = f"""
      You are an AI assistant serving as a SQL expert for BigQuery.
      Your job is to help users generate SQL answers from natural language questions (inside Nl2sqlInput).
      You should produce the result as NL2SQLOutput.

      Use the provided tools to help generate the most accurate SQL:
      1. First, use {db_tool_name} tool to generate initial SQL from the question.
      2. Then you should use the execute_sql tool to validate and execute the SQL. If there are any errors with the SQL, you should go back to step 1 and recreate the SQL by addressing the error.
      4. Generate the final result in JSON format with four keys: "explain", "sql", "sql_results", "nl_results".
          "explain": "write out step-by-step reasoning to explain how you are generating the query based on the schema, example, and question.",
          "sql": "Output your generated SQL!",
          "sql_results": "raw sql execution query_result from execute_sql if it's available, otherwise None",
          "nl_results": "Natural language about results, otherwise it's None if generated SQL is invalid"
      
      You should pass one tool call to another tool call as needed!

      NOTE: you should ALWAYS USE THE TOOL {db_tool_name} to generate SQL, not make up SQL WITHOUT CALLING TOOLS.
      Keep in mind that you are an orchestration agent, not a SQL expert, so use the tools to help you generate SQL, but do not make up SQL.

      NOTE: you must ALWAYS PASS the project_id {get_env_var("BQ_COMPUTE_PROJECT_ID")} to the execute_sql tool. DO NOT pass any other project id.

    """

    return instruction_prompt_bigquery

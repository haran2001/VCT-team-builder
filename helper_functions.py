import json
import os
import sqlite3
import uuid
import streamlit as st
from dotenv import load_dotenv  # Import load_dotenv
from services import bedrock_agent_runtime  # Ensure this module is accessible

import logging

from botocore.exceptions import ClientError

import boto3
# Load environment variables from .env file
load_dotenv()

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with the Amazon Bedrock Agents Runtime
client to send prompts to an agent to process and respond to.
"""


logger = logging.getLogger(__name__)


# snippet-start:[python.example_code.bedrock-agent-runtime.BedrockAgentsRuntimeWrapper.class]
# snippet-start:[python.example_code.bedrock-agent-runtime.BedrockAgentRuntimeWrapper.decl]
class BedrockAgentRuntimeWrapper:
    """Encapsulates Amazon Bedrock Agents Runtime actions."""

    def __init__(self, runtime_client):
        """
        :param runtime_client: A low-level client representing the Amazon Bedrock Agents Runtime.
                               Describes the API operations for running
                               inferences using Bedrock Agents.
        """
        self.agents_runtime_client = runtime_client

    # snippet-end:[python.example_code.bedrock-agent-runtime.BedrockAgentRuntimeWrapper.decl]

    # snippet-start:[python.example_code.bedrock-agent-runtime.InvokeAgent]
    def invoke_agent(self, agent_id, agent_alias_id, session_id, prompt):
        """
        Sends a prompt for the agent to process and respond to.

        :param agent_id: The unique identifier of the agent to use.
        :param agent_alias_id: The alias of the agent to use.
        :param session_id: The unique identifier of the session. Use the same value across requests
                           to continue the same conversation.
        :param prompt: The prompt that you want Claude to complete.
        :return: Inference response from the model.
        """

        try:
            # Note: The execution time depends on the foundation model, complexity of the agent,
            # and the length of the prompt. In some cases, it can take up to a minute or more to
            # generate a response.
            response = self.agents_runtime_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
            )

            completion = ""

            for event in response.get("completion"):
                chunk = event["chunk"]
                completion = completion + chunk["bytes"].decode()

        except ClientError as e:
            logger.error(f"Couldn't invoke agent. {e}")
            raise

        return completion
        # return response

    # snippet-end:[python.example_code.bedrock-agent-runtime.InvokeAgent]

# snippet-end:[python.example_code.bedrock-agent-runtime.BedrockAgentsRuntimeWrapper.class]


# # Create a low-level client for the Bedrock Agents Runtime
# runtime_client = boto3.client("bedrock-agent-runtime", 
#                               region_name="us-west-2",
#                               aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#                               aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
# )
# # Initialize the wrapper
# bedrock_wrapper = BedrockAgentRuntimeWrapper(runtime_client)

# # Invoke the agent with a prompt

# # Get configuration from environment variables
# agent_id = "O7CRGIZT2S"
# agent_alias_id = "XE2H3UOISM"
# session_id = "s1"
# prompt = "what is valorant?"

# try:
#     print('hello world')
#     response = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, prompt)
#     print(f"Agent Response: {response}")
# except ClientError as error:
#     print(f"Error invoking agent: {error}")

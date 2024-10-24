import json
import os
import sqlite3
import uuid
import streamlit as st
from dotenv import load_dotenv  
from helper_functions import BedrockAgentRuntimeWrapper
import boto3
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
agent_id = os.environ.get("BEDROCK_AGENT_ID")
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")  # Default test alias ID
ui_title = os.environ.get("BEDROCK_AGENT_TEST_UI_TITLE", "VALORANT Team Builder")
ui_icon = os.environ.get("BEDROCK_AGENT_TEST_UI_ICON", "🎮")  # Default icon
region = os.environ.get("BEDROCK_REGION")  # Load the region
session_id = "s1"

# Database configuration
DATABASE = "valorant_players.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: SQLite database connection.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn

def init_state():
    """
    Initializes the Streamlit session state variables.
    """
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.citations = []
    st.session_state.trace = {}
    st.session_state.team_composition = ""

# Define role categories
ROLE_CATEGORIES = {
    "Duelist": ["Jett", "Phoenix", "Reyna", "Raze", "Yoru", "Neon"],
    "Sentinel": ["Sage", "Cypher", "Killjoy", "Viper"],
    "Controller": ["Omen", "Astra", "Brimstone", "Viper"],
    "Initiator": ["Sova", "Breach", "Skye", "KAY/O", "Fade"],
}

def assign_role(agent):
    """
    Assigns a role based on the agent name.
    
    Args:
        agent (str): Name of the agent.
    
    Returns:
        str: Assigned role (Duelist, Sentinel, Controller, Initiator, or Undefined).
    """
    for role, agents in ROLE_CATEGORIES.items():
        if agent in agents:
            return role
    return "Undefined"

def build_prompt(team_type, additional_constraints, players):
    """
    Builds the prompt to send to OpenAI based on the team type and constraints.
    
    Args:
        team_type (str): Description of the team submission type.
        additional_constraints (str): Any additional constraints provided by the user.
        players (list of dict): List of player data dictionaries.
    
    Returns:
        str: The constructed prompt.
    """
    # Convert player data to a readable format
    player_info = ""
    for player in players:
        role = assign_role(player["agent"])
        region = player['region'].upper() if player['region'] else "UNKNOWN"
        
        player_info += (
            f"Player Name: {player['player']}\n"
            f"Organization: {player['org']}\n"
            f"Rounds Played: {player['rds']}\n"
            f"Average Combat Score: {player['average_combat_score']}\n"
            f"Kill/Death Ratio: {player['kill_deaths']}\n"
            f"Average Damage Per Round: {player['average_damage_per_round']}\n"
            f"Kills Per Round: {player['kills_per_round']}\n"
            f"Assists Per Round: {player['assists_per_round']}\n"
            f"First Kills Per Round: {player['first_kills_per_round']}\n"
            f"First Deaths Per Round: {player['first_deaths_per_round']}\n"
            f"Headshot Percentage: {player['headshot_percentage']}%\n"
            f"Clutch Success Percentage: {player['clutch_success_percentage']}%\n"
            f"Clutches Won/Played: {player['clutch_won_played']:.2f}\n"
            f"Total Kills: {player['total_kills']}\n"
            f"Total Deaths: {player['total_deaths']}\n"
            f"Total Assists: {player['total_assists']}\n"
            f"Total First Kills: {player['total_first_kills']}\n"
            f"Total First Deaths: {player['total_first_deaths']}\n"
            f"Map ID: {player['map_id']}\n"
            f"Agent: {player['agent']} ({role})\n"
            f"Region: {region}\n"
            "-----\n"
        )

    prompt = (
        f"Build a team for a VALORANT esports team based on the following player data:\n\n"
        f"{player_info}\n\n"
        f"Team Submission Type: {team_type}\n"
    )

    if additional_constraints:
        prompt += f"Additional Constraints: {additional_constraints}\n\n"

    prompt += (
        "For each team composition, perform the following tasks:\n"
        "1. Assign roles to each player on the team and explain their contribution.\n"
        "2. Specify Offensive vs. Defensive roles.\n"
        "3. Categorize each agent (Duelist, Sentinel, Controller, Initiator).\n"
        "4. Assign a team IGL (In-Game Leader) and explain their role as the primary strategist and shotcaller.\n"
        "5. Provide insights on team strategy and hypothesize team strengths and weaknesses.\n"
    )

    return prompt

def fetch_players(team_type):
    """
    Fetches players from the database based on the selected team submission type.
    
    Args:
        team_type (str): Selected team submission type.
    
    Returns:
        list of dict: List of players matching the criteria.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if team_type == "Professional Team Submission":
            query = """
            SELECT * FROM players
            WHERE org IN ('Ascend', 'Mystic', 'Legion', 'Phantom', 'Rising', 'Nebula', 'OrgZ', 'T1A')
            """
        elif team_type == "Semi-Professional Team Submission":
            query = """
            SELECT * FROM players
            WHERE org = 'Rising'
            """
        elif team_type == "Game Changers Team Submission":
            query = """
            SELECT * FROM players
            WHERE org = 'OrgZ'
            """
        elif team_type == "Mixed-Gender Team Submission":
            query = """
            SELECT * FROM players
            WHERE org = 'OrgZ'
            LIMIT 1
            """
        elif team_type == "Cross-Regional Team Submission":
            query = """
            SELECT * FROM players
            WHERE region IN ('Japan', 'Russia', 'China', 'ME', 'LATAM')
            LIMIT 3
            """
        elif team_type == "Rising Star Team Submission":
            query = """
            SELECT * FROM players
            WHERE org = 'Rising'
            """
        else:
            st.error("Invalid team submission type selected.")
            return []

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            st.error("No players found matching the selected criteria. Please try a different team submission type.")
            return []

        players = [dict(row) for row in rows]
        return players

    except Exception as e:
        conn.close()
        st.error(f"An error occurred while querying the database: {e}")
        return []

def validate_constraints(team_type, players):
    """
    Validates additional constraints based on the team submission type.
    
    Args:
        team_type (str): Selected team submission type.
        players (list of dict): List of players fetched from the database.
    
    Returns:
        bool: True if constraints are met, False otherwise.
    """
    if team_type == "Mixed-Gender Team Submission":
        orgZ_players = [p for p in players if p["org"] == "OrgZ"]
        if len(orgZ_players) < 1:
            st.error("Not enough players from underrepresented groups (OrgZ) to build a Mixed-Gender team.")
            return False
    elif team_type == "Cross-Regional Team Submission":
        regions = set(p["region"].upper() for p in players if isinstance(p["region"], str))
        if len(regions) < 3:
            st.error("Not enough players from different regions to build a Cross-Regional team.")
            return False
    return True

def generate_team(team_type, additional_constraints, players):
    """
    Generates the team composition using OpenAI's GPT-4 via bedrock_agent_runtime.
    
    Args:
        team_type (str): Selected team submission type.
        additional_constraints (str): Any additional constraints provided by the user.
        players (list of dict): List of players fetched from the database.
    
    Returns:
        str: Generated team composition.
    """
    prompt = build_prompt(team_type, additional_constraints, players)

    try:
        runtime_client = boto3.client("bedrock-agent-runtime", 
                                    region_name="us-west-2",
                                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        # Initialize the wrapper
        bedrock_wrapper = BedrockAgentRuntimeWrapper(runtime_client)

        try:
            # print('hello world')
            output_text = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, prompt)
            print(f"Agent Response: {output_text}")

        except ClientError as error:
            print(f"Error invoking agent: {error}")

        return output_text

    except Exception as e:
        st.error(f"An error occurred while generating the team: {e}")
        return ""

def display_trace_and_citations():
    """
    Displays trace and citation information in the sidebar.
    """
    trace_types_map = {
        "Pre-Processing": ["preGuardrailTrace", "preProcessingTrace"],
        "Orchestration": ["orchestrationTrace"],
        "Post-Processing": ["postProcessingTrace", "postGuardrailTrace"]
    }

    trace_info_types_map = {
        "preProcessingTrace": ["modelInvocationInput", "modelInvocationOutput"],
        "orchestrationTrace": ["invocationInput", "modelInvocationInput", "modelInvocationOutput", "observation", "rationale"],
        "postProcessingTrace": ["modelInvocationInput", "modelInvocationOutput", "observation"]
    }

    with st.sidebar:
        st.title("Trace & Citations")
        st.markdown("---")
        st.subheader("Trace")

        step_num = 1
        has_trace = False
        for trace_type_header, trace_types in trace_types_map.items():
            st.markdown(f"### {trace_type_header}")
            for trace_type in trace_types:
                if trace_type in st.session_state.trace:
                    has_trace = True
                    trace_steps = {}

                    for trace in st.session_state.trace[trace_type]:
                        if trace_type in trace_info_types_map:
                            trace_info_types = trace_info_types_map[trace_type]
                            for trace_info_type in trace_info_types:
                                if trace_info_type in trace:
                                    trace_id = trace[trace_info_type]["traceId"]
                                    if trace_id not in trace_steps:
                                        trace_steps[trace_id] = [trace]
                                    else:
                                        trace_steps[trace_id].append(trace)
                                    break
                        else:
                            trace_id = trace["traceId"]
                            trace_steps[trace_id] = [
                                {
                                    trace_type: trace
                                }
                            ]

                    # Show trace steps in JSON similar to the Bedrock console
                    for trace_id in trace_steps.keys():
                        with st.expander(f"Trace Step {step_num}", expanded=False):
                            for trace in trace_steps[trace_id]:
                                trace_str = json.dumps(trace, indent=2)
                                st.code(trace_str, language="json")
                        step_num += 1
        if not has_trace:
            st.text("No trace information available.")

        st.markdown("---")
        st.subheader("Citations")
        if st.session_state.citations:
            citation_num = 1
            for citation in st.session_state.citations:
                for retrieved_ref in citation.get("retrievedReferences", []):
                    with st.expander(f"Citation [{citation_num}]", expanded=False):
                        citation_content = {
                            "generatedResponsePart": citation.get("generatedResponsePart", {}),
                            "retrievedReference": retrieved_ref
                        }
                        citation_str = json.dumps(citation_content, indent=2)
                        st.code(citation_str, language="json")
                    citation_num += 1
        else:
            st.text("No citations available.")

def main():
    """
    Main function to run the Streamlit app.
    """
    # General page configuration and initialization
    st.set_page_config(page_title=ui_title, page_icon=ui_icon, layout="wide")
    st.title(ui_title)
    st.markdown("Generate and analyze VALORANT team compositions based on player data.")

    if "session_id" not in st.session_state:
        init_state()

    # Sidebar button to reset session state
    with st.sidebar:
        if st.button("Reset Session"):
            init_state()
            st.experimental_rerun()

    # Team Submission Form
    st.header("Build Your Team")
    with st.form("team_form"):
        team_type = st.selectbox(
            "Select Team Submission Type:",
            [
                "Professional Team Submission",
                "Semi-Professional Team Submission",
                "Game Changers Team Submission",
                "Mixed-Gender Team Submission",
                "Cross-Regional Team Submission",
                "Rising Star Team Submission"
            ],
            help="Choose the type of team you want to build."
        )
        additional_constraints = st.text_area(
            "Additional Constraints (Optional):",
            placeholder="Enter any additional constraints or leave blank."
        )
        submit_button = st.form_submit_button(label="Build Team")

    if submit_button:
        players = fetch_players(team_type)
        print(players)
        if players and validate_constraints(team_type, players):
            with st.spinner("Generating team composition..."):
                team_composition = generate_team(team_type, additional_constraints, players)
                if team_composition:
                    st.success("Team composition generated successfully!")
                    st.markdown("### Team Composition")
                    st.markdown(team_composition, unsafe_allow_html=True)

    # Display Trace and Citations in Sidebar
    display_trace_and_citations()

if __name__ == "__main__":
    main()
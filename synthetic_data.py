#!/usr/bin/env python3
"""
Script to generate synthetic VALORANT player data and export it as a CSV file.

Usage:
    python generate_synthetic_valorant_data.py --output_csv synthetic_valorant_players.csv --num_players 1000
"""

import pandas as pd
import numpy as np
from faker import Faker
import argparse
import random
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        args: Parsed arguments containing output CSV path and number of players.
    """
    parser = argparse.ArgumentParser(
        description="Generate synthetic VALORANT player data."
    )
    parser.add_argument(
        "--output_csv",
        type=str,
        default="synthetic_valorant_players.csv",
        help="Path to the output CSV file.",
    )
    parser.add_argument(
        "--num_players",
        type=int,
        default=1000,
        help="Number of synthetic players to generate.",
    )

    args = parser.parse_args()
    return args


def get_agents_by_role():
    """
    Returns a dictionary categorizing VALORANT agents by their roles.

    Returns:
        dict: Agents categorized by role.
    """
    return {
        "Duelist": ["Jett", "Phoenix", "Reyna", "Raze", "Yoru", "Neon"],
        "Sentinel": ["Sage", "Cypher", "Killjoy"],
        "Controller": ["Omen", "Astra", "Brimstone", "Viper"],
        "Initiator": ["Sova", "Breach", "Skye", "KAY/O", "Fade"],
    }


def get_random_agent(agents_by_role):
    """
    Randomly selects an agent from the provided agents dictionary, ensuring role distribution.

    Args:
        agents_by_role (dict): Agents categorized by role.

    Returns:
        tuple: Selected agent and their role.
    """
    role = random.choice(list(agents_by_role.keys()))
    agent = random.choice(agents_by_role[role])
    return agent, role


def get_organizations():
    """
    Returns a list of fictional VALORANT organizations.

    Returns:
        list: List of organization names.
    """
    return [
        "T1A",
        "OrgY",
        "OrgZ",
        "Infinity",
        "Eclipse",
        "Nova",
        "Spectre",
        "Phantom",
        "Vanguard",
        "Sentinel",
        "Revolution",
        "Ascend",
        "Legion",
        "Dominion",
        "Harmony",
        "Titan",
        "Nebula",
        "Mirage",
        "Radiant",
        "Pulse",
        "Fusion",
        "Aegis",
        "Valor",
        "Mystic",
        "Storm",
        "Obsidian",
        "Zenith",
        "Rising",
        "Pulse",
        "Quantum",
    ]


def get_regions():
    """
    Returns a list of regions.

    Returns:
        list: List of region codes.
    """
    return [
        "NA",
        "EU",
        "ASIA",
        "LATAM",
        "Oceania",
        "ME",
        "Russia",
        "India",
        "China",
        "Japan",
    ]


def generate_player_data(num_players):
    """
    Generates synthetic player data.

    Args:
        num_players (int): Number of players to generate.

    Returns:
        pd.DataFrame: DataFrame containing synthetic player data.
    """
    logging.info(f"Generating synthetic data for {num_players} players...")
    fake = Faker()
    Faker.seed(0)
    np.random.seed(0)
    random.seed(0)

    agents_by_role = get_agents_by_role()
    organizations = get_organizations()
    regions = get_regions()
    maps = ["Bind", "Haven", "Split", "Ascent", "Icebox", "Breeze", "Fracture"]
    map_ids = {map_name: idx + 1 for idx, map_name in enumerate(maps)}

    data = {
        "player": [],
        "org": [],
        "rds": [],
        "average_combat_score": [],
        "kill_deaths": [],
        "average_damage_per_round": [],
        "kills_per_round": [],
        "assists_per_round": [],
        "first_kills_per_round": [],
        "first_deaths_per_round": [],
        "headshot_percentage": [],
        "clutch_success_percentage": [],
        "clutch_won_played": [],
        "total_kills": [],
        "total_deaths": [],
        "total_assists": [],
        "total_first_kills": [],
        "total_first_deaths": [],
        "map_id": [],
        "agent": [],
        "region": [],
    }

    for _ in range(num_players):
        # Generate player name
        player_name = (
            fake.unique.user_name().replace(".", "").replace("_", "").capitalize()
        )

        # Assign organization
        org = random.choice(organizations)

        # Assign region
        region = random.choice(regions)

        # Assign agent and role
        agent, role = get_random_agent(agents_by_role)

        # Assign map_id
        map_name = random.choice(maps)
        map_id = map_ids[map_name]

        # Generate statistics based on role
        # These ranges can be adjusted to better simulate realistic data
        rds = random.randint(100, 500)

        if role == "Duelist":
            average_combat_score = round(np.random.normal(300, 30), 1)
            kill_deaths = round(np.random.normal(1.5, 0.3), 2)
            average_damage_per_round = round(np.random.normal(180, 20), 1)
            kills_per_round = round(np.random.normal(1.5, 0.3), 2)
            assists_per_round = round(np.random.normal(0.3, 0.1), 2)
            first_kills_per_round = round(np.random.uniform(0.1, 0.4), 2)
            first_deaths_per_round = round(np.random.uniform(0.0, 0.2), 2)
            headshot_percentage = round(np.random.uniform(25, 55), 1)
            clutch_success_percentage = round(np.random.uniform(15, 65), 1)
        elif role == "Sentinel":
            average_combat_score = round(np.random.normal(290, 25), 1)
            kill_deaths = round(np.random.normal(1.2, 0.25), 2)
            average_damage_per_round = round(np.random.normal(160, 15), 1)
            kills_per_round = round(np.random.normal(0.8, 0.2), 2)
            assists_per_round = round(np.random.normal(0.5, 0.15), 2)
            first_kills_per_round = round(np.random.uniform(0.0, 0.3), 2)
            first_deaths_per_round = round(np.random.uniform(0.0, 0.25), 2)
            headshot_percentage = round(np.random.uniform(20, 50), 1)
            clutch_success_percentage = round(np.random.uniform(10, 60), 1)
        elif role == "Controller":
            average_combat_score = round(np.random.normal(295, 28), 1)
            kill_deaths = round(np.random.normal(1.3, 0.28), 2)
            average_damage_per_round = round(np.random.normal(170, 18), 1)
            kills_per_round = round(np.random.normal(0.9, 0.25), 2)
            assists_per_round = round(np.random.normal(0.4, 0.12), 2)
            first_kills_per_round = round(np.random.uniform(0.05, 0.25), 2)
            first_deaths_per_round = round(np.random.uniform(0.0, 0.15), 2)
            headshot_percentage = round(np.random.uniform(15, 45), 1)
            clutch_success_percentage = round(np.random.uniform(10, 55), 1)
        elif role == "Initiator":
            average_combat_score = round(np.random.normal(305, 32), 1)
            kill_deaths = round(np.random.normal(1.4, 0.35), 2)
            average_damage_per_round = round(np.random.normal(175, 22), 1)
            kills_per_round = round(np.random.normal(1.0, 0.25), 2)
            assists_per_round = round(np.random.normal(0.6, 0.18), 2)
            first_kills_per_round = round(np.random.uniform(0.15, 0.35), 2)
            first_deaths_per_round = round(np.random.uniform(0.05, 0.2), 2)
            headshot_percentage = round(np.random.uniform(20, 50), 1)
            clutch_success_percentage = round(np.random.uniform(20, 70), 1)
        else:
            # Default values if role is undefined
            average_combat_score = round(np.random.normal(280, 25), 1)
            kill_deaths = round(np.random.normal(1.0, 0.3), 2)
            average_damage_per_round = round(np.random.normal(150, 20), 1)
            kills_per_round = round(np.random.normal(0.7, 0.2), 2)
            assists_per_round = round(np.random.normal(0.3, 0.1), 2)
            first_kills_per_round = round(np.random.uniform(0.0, 0.2), 2)
            first_deaths_per_round = round(np.random.uniform(0.0, 0.1), 2)
            headshot_percentage = round(np.random.uniform(10, 40), 1)
            clutch_success_percentage = round(np.random.uniform(5, 50), 1)

        # Ensure no negative statistics
        kill_deaths = max(kill_deaths, 0.1)
        clutch_won_played = round(np.random.uniform(0.0, 1.0), 2)

        # Calculate total statistics
        total_kills = int(round(kills_per_round * rds))
        total_deaths = int(round(kill_deaths * rds))
        total_assists = int(round(assists_per_round * rds))
        total_first_kills = int(round(first_kills_per_round * rds))
        total_first_deaths = int(round(first_deaths_per_round * rds))

        # Append data
        data["player"].append(player_name)
        data["org"].append(org)
        data["rds"].append(rds)
        data["average_combat_score"].append(average_combat_score)
        data["kill_deaths"].append(kill_deaths)
        data["average_damage_per_round"].append(average_damage_per_round)
        data["kills_per_round"].append(kills_per_round)
        data["assists_per_round"].append(assists_per_round)
        data["first_kills_per_round"].append(first_kills_per_round)
        data["first_deaths_per_round"].append(first_deaths_per_round)
        data["headshot_percentage"].append(headshot_percentage)
        data["clutch_success_percentage"].append(clutch_success_percentage)
        data["clutch_won_played"].append(clutch_won_played)
        data["total_kills"].append(total_kills)
        data["total_deaths"].append(total_deaths)
        data["total_assists"].append(total_assists)
        data["total_first_kills"].append(total_first_kills)
        data["total_first_deaths"].append(total_first_deaths)
        data["map_id"].append(map_id)
        data["agent"].append(agent)
        data["region"].append(region)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Shuffle the DataFrame to ensure random distribution
    df = df.sample(frac=1).reset_index(drop=True)

    # Save to CSV
    return df


def main():
    # Parse command-line arguments
    args = parse_arguments()
    output_csv = args.output_csv
    num_players = args.num_players

    # Generate synthetic player data
    df = generate_player_data(num_players)

    # Save to CSV
    logging.info(f"Saving synthetic data to {output_csv}...")
    df.to_csv(output_csv, index=False)
    logging.info("Data generation completed successfully.")


if __name__ == "__main__":
    main()

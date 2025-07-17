#!/usr/bin/env python3

def generate_sql_from_missions():
    """Read Missions.txt and generate SQL to replace all challenges"""
    
    # Read all challenges from Missions.txt
    with open('Missions.txt', 'r') as f:
        challenges = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(challenges)} challenges in Missions.txt")
    
    # Generate SQL file
    with open('use_missions_txt_challenges.sql', 'w') as f:
        f.write("-- Clear existing challenges and replace with Missions.txt challenges\n")
        f.write("DELETE FROM challenges;\n\n")
        f.write("-- Insert all challenges from Missions.txt\n")
        f.write("INSERT INTO challenges (description, category) VALUES\n")
        
        for i, challenge in enumerate(challenges):
            # Escape single quotes in the challenge text
            challenge_escaped = challenge.replace("'", "''")
            
            if i == len(challenges) - 1:
                # Last challenge - no comma
                f.write(f"('{challenge_escaped}', 'Social');\n")
            else:
                f.write(f"('{challenge_escaped}', 'Social'),\n")
    
    print("Generated use_missions_txt_challenges.sql successfully!")

if __name__ == "__main__":
    generate_sql_from_missions() 
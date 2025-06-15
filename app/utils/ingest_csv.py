import pandas as pd
import re
from app.db.session import SessionLocal, engine
from app.db.models import Base, Team, Player

# Create all tables (safe if already done via Alembic)
Base.metadata.create_all(bind=engine)

# Read CSV
df = pd.read_csv("FootballPlayers.csv")

# Clean age field to extract integer
def extract_age(age_str):
    match = re.search(r"\d+", age_str)
    return int(match.group()) if match else None

# Start DB session
db = SessionLocal()

# Track added teams to avoid duplicates
team_cache = {}

# Iterate over each player
for _, row in df.iterrows():
    team_name = row["Current Team"]
    
    # Check if team already exists in DB
    existing_team = db.query(Team).filter_by(name=team_name).first()

    if existing_team:
        team = existing_team
    else:
        team = Team(name=team_name)
        db.add(team)
        db.commit()
        db.refresh(team)

    # Create Player record
    player = Player(
        name=row["Name"],
        age=extract_age(row["Age"]),
        nationality=row["Nationality"],
        position=row["PositionsSummary"],
        appearances=row["Apps"],
        minutes=row["Mins"],
        goals=row["Goals"],
        assists=row["Assists"],
        yellow_cards=row["Yel"],
        red_cards=row["Red"],
        shots_per_game=row["SpG"],
        pass_success=row["PS%"],
        aerials_won=row["AerialsWon"],
        motm=row["MotM"],
        rating=row["Rating"],
        team_id=team.id
    )
    
    db.add(player)

# Commit all changes
db.commit()
db.close()

print("✅ Data successfully ingested from CSV.")
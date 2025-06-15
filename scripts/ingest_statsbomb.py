import os
import json
import sys
from datetime import datetime

# Setup for absolute import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Team, Player, MatchStat

# Update this to use the sample folder
BASE_DIR = "data/statsbomb/sample"
MATCHES_DIR = os.path.join(BASE_DIR, "matches")
EVENTS_DIR = os.path.join(BASE_DIR, "events")

def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return []

def get_team(name, db: Session):
    team = db.query(Team).filter_by(name=name).first()
    if not team:
        team = Team(name=name)
        db.add(team)
        db.commit()
        db.refresh(team)
    return team

def get_player(name, team_id, db: Session):
    player = db.query(Player).filter_by(name=name, team_id=team_id).first()
    if not player:
        player = Player(name=name, team_id=team_id)
        db.add(player)
        db.commit()
        db.refresh(player)
    return player

def ingest_match(match, db: Session):
    match_id = match["match_id"]
    match_date = datetime.strptime(match["match_date"], "%Y-%m-%d").date()

    home_team_name = match["home_team"]["home_team_name"]
    away_team_name = match["away_team"]["away_team_name"]

    event_file = os.path.join(EVENTS_DIR, f"{match_id}.json")
    if not os.path.exists(event_file):
        print(f"⚠️ Skipping match {match_id} — event file missing.")
        return

    print(f"📥 Ingesting Match {match_id}: {home_team_name} vs {away_team_name}")
    events = load_json(event_file)

    player_stats = {}

    for event in events:
        if event.get("type", {}).get("name") != "Pass":
            continue
        player_info = event.get("player")
        if not player_info:
            continue

        player_name = player_info.get("name")
        team_name = event.get("team", {}).get("name")
        team = get_team(team_name, db)
        player = get_player(player_name, team.id, db)

        key = player.id
        player_stats.setdefault(key, {"passes": 0, "passes_completed": 0, "goals": 0, "assists": 0})

        player_stats[key]["passes"] += 1
        if event.get("pass", {}).get("outcome") is None:
            player_stats[key]["passes_completed"] += 1
        if event.get("pass", {}).get("goal_assist"):
            player_stats[key]["assists"] += 1

    for player_id, stats in player_stats.items():
        accuracy = (stats["passes_completed"] / stats["passes"]) * 100 if stats["passes"] else 0
        match_stat = MatchStat(
            player_id=player_id,
            match_date=match_date,
            goals=stats["goals"],
            assists=stats["assists"],
            pass_accuracy=round(accuracy, 2)
        )
        db.add(match_stat)

    db.commit()
    print(f"✅ Match {match_id} committed.")

def main():
    db: Session = SessionLocal()
    print("🚀 Ingesting from minimal sample folder...")

    for match_file in os.listdir(MATCHES_DIR):
        if not match_file.endswith(".json"):
            continue

        match_path = os.path.join(MATCHES_DIR, match_file)
        print(f"\n📂 Processing: {match_path}")
        matches = load_json(match_path)

        for match in matches:
            ingest_match(match, db)

    db.close()
    print("\n🎉 Ingestion complete.")

if __name__ == "__main__":
    main()

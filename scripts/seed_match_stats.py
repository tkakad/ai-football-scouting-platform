import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Player, MatchStat
from datetime import date

def seed_match_stats():
    db: Session = SessionLocal()

    # Get or create Jude Bellingham
    player = db.query(Player).filter(Player.name == "Jude Bellingham").first()
    if not player:
        print("Creating dummy player: Jude Bellingham")
        player = Player(
            name="Jude Bellingham",
            age=20,
            nationality="England",
            position="Midfielder",
            appearances=25,
            minutes=2100,
            goals=8,
            assists=6,
            yellow_cards=2,
            red_cards=0,
            shots_per_game=2.1,
            pass_success=87.3,
            aerials_won=1.5,
            motm=5,
            rating=7.8,
            team_id=1
        )
        db.add(player)
        db.commit()
        db.refresh(player)

    # Add dummy match stat for Jude
    match_stat = db.query(MatchStat).filter_by(player_id=player.id).first()
    if not match_stat:
        match_stat = MatchStat(
            player_id=player.id,
            match_date=date(2024, 5, 10),
            goals=1,
            assists=1,
            pass_accuracy=87.0
        )
        db.add(match_stat)
        db.commit()
        print("✅ Match stat for Jude Bellingham inserted.")
    else:
        print("ℹ️ Jude Bellingham match stat already exists.")

    # Get or create Pedri
    pedri = db.query(Player).filter(Player.name == "Pedri").first()
    if not pedri:
        print("Creating dummy player: Pedri")
        pedri = Player(
            name="Pedri",
            age=21,
            nationality="Spain",
            position="Midfielder",
            appearances=23,
            minutes=1850,
            goals=5,
            assists=4,
            yellow_cards=1,
            red_cards=0,
            shots_per_game=1.8,
            pass_success=89.2,
            aerials_won=0.7,
            motm=3,
            rating=7.2,
            team_id=1
        )
        db.add(pedri)
        db.commit()
        db.refresh(pedri)

    # Add dummy match stat for Pedri
    pedri_stat = db.query(MatchStat).filter_by(player_id=pedri.id).first()
    if not pedri_stat:
        pedri_stat = MatchStat(
            player_id=pedri.id,
            match_date=date(2024, 5, 11),
            goals=0,
            assists=2,
            pass_accuracy=89.0
        )
        db.add(pedri_stat)
        db.commit()
        print("✅ Match stat for Pedri inserted.")
    else:
        print("ℹ️ Pedri match stat already exists.")

    db.close()

if __name__ == "__main__":
    seed_match_stats()

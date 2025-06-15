from sqlalchemy.orm import Session
from app.db.models import Player, MatchStat, Team
import re

def generate_insight(prompt: str, context: str, db: Session) -> str:
    # Extract player name by searching for known names (simplified approach)
    all_players = db.query(Player).all()
    player = None
    for p in all_players:
        if p.name.lower() in prompt.lower():
            player = p
            break

    if not player:
        return "Sorry, I couldn't identify the player in your request."

    # Fetch latest match stat for player
    match_stat = (
        db.query(MatchStat)
        .filter(MatchStat.player_id == player.id)
        .order_by(MatchStat.match_date.desc())
        .first()
    )

    if not match_stat:
        return f"No match statistics found for {player.name}."

    return (
        f"{player.name} scored {match_stat.goals} goal(s) and had "
        f"{match_stat.pass_accuracy}% pass accuracy on {match_stat.match_date.strftime('%Y-%m-%d')}."
    )
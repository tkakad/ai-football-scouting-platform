from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.models import Player, FactBiometricMinute, Team
from app.utils.timestamp import format_timestamp


def get_trending_players(db: Session, timezone: str = "UTC", limit: int = 5):
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    # Fetch biometric stats per player over the last week
    player_data = (
        db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.rating.label("avg_rating"),
            Team.name.label("team_name"),
            Player.position.label("position"),
            func.avg(FactBiometricMinute.sprint_count).label("avg_sprint"),
            func.avg(FactBiometricMinute.heart_rate_variability).label("avg_hrv")
        )
        .join(FactBiometricMinute, FactBiometricMinute.player_id == Player.id)
        .join(Team, Player.team_id == Team.id)
        .filter(FactBiometricMinute.timestamp >= one_week_ago)
        .group_by(Player.id, Team.name)
        .order_by(func.avg(FactBiometricMinute.sprint_count).desc())
        .limit(limit)
        .all()
    )

    trending = []
    for p in player_data:
        trending.append({
            "player_id": p.player_id,
            "name": p.player_name,
            "team": p.team_name,
            "position": p.position,
            "avg_rating": round(p.avg_rating or 0, 2),
            "sprint_change_pct": round((p.avg_sprint or 0) / 10 * 100, 2),
            "hrv_change_pct": round((p.avg_hrv or 0) / 100 * 100, 2),
            "confidence": round(min(1.0, (p.avg_sprint or 0) / 10), 2),
            "generated_at": format_timestamp(timezone)
        })

    return trending

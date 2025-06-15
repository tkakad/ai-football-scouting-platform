from sqlalchemy.orm import Session
from app.db.models import Player

COMPARISON_FIELDS = [
    "goals", "assists", "rating", "minutes", "appearances",
    "pass_success", "shots_per_game", "motm", "aerials_won"
]

def compare_players(name1: str, name2: str, db: Session) -> dict:
    p1 = db.query(Player).filter(Player.name.ilike(f"%{name1}%")).first()
    p2 = db.query(Player).filter(Player.name.ilike(f"%{name2}%")).first()

    if not p1 or not p2:
        return {
            "error": "One or both players not found",
            "found": {
                "player1": bool(p1),
                "player2": bool(p2)
            }
        }

    def extract(player):
        return {field: getattr(player, field, None) for field in COMPARISON_FIELDS}

    p1_stats = extract(p1)
    p2_stats = extract(p2)

    comparison_results = {}
    win_counts = {p1.name: 0, p2.name: 0, "tie": 0}

    for field in COMPARISON_FIELDS:
        val1 = p1_stats.get(field)
        val2 = p2_stats.get(field)
        if val1 is None or val2 is None:
            continue

        delta = round(val1 - val2, 2)
        winner = (
            p1.name if delta > 0 else
            p2.name if delta < 0 else
            "tie"
        )
        win_counts[winner] += 1

        comparison_results[field] = {
            "player1": val1,
            "player2": val2,
            "delta": abs(delta),
            "winner": winner
        }

    # Build summary string
    summary_lines = []
    for field, result in comparison_results.items():
        line = f"{result['winner']} leads in {field} by {result['delta']}." if result['winner'] != "tie" else f"Both are equal in {field}."
        summary_lines.append(line)
    
    winner_overall = max((p1.name, p2.name), key=lambda x: win_counts[x])
    overall_summary = (
        f"{p1.name} vs {p2.name} comparison: "
        f"{winner_overall} leads in {win_counts[winner_overall]} out of {len(COMPARISON_FIELDS)} metrics."
    )

    return {
        "player1": {"name": p1.name, "stats": p1_stats},
        "player2": {"name": p2.name, "stats": p2_stats},
        "comparison": comparison_results,
        "summary": {
            "winner": winner_overall,
            "line_summary": summary_lines,
            "overall": overall_summary
        }
    }

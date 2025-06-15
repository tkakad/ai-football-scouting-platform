from sqlalchemy.orm import Session
from app.db.models import Player
from typing import List

# Basic keyword-to-position parser
def parse_question_and_search(db: Session, question: str) -> List[Player]:
    keywords = {
        "goalkeeper": "Goalkeeper",
        "defender": "Defender",
        "midfielder": "Midfielder",
        "attacker": "Attacking",
        "forward": "Attacking",
        "striker": "Attacking",
    }

    # Lowercase and match keyword
    position = None
    for k, v in keywords.items():
        if k in question.lower():
            position = v
            break

    query = db.query(Player)
    if position:
        query = query.filter(Player.position.ilike(f"%{position}%"))

    # Order by rating descending
    return query.order_by(Player.rating.desc()).limit(10).all()

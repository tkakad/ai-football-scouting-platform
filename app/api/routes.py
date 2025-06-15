import uuid
from random import uniform, randint
from decimal import Decimal
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.db.models import Player, Team, FeedbackLog, SearchLog, ChatPromptLog, MatchStat
from app.db.session import SessionLocal
from app.utils.timestamp import format_timestamp
from app.utils.trending import get_trending_players
from app.services.chat_router import classify_prompt
from app.services.insight_generator import generate_insight
from app.services.player_comparator import compare_players

router = APIRouter()

# -------------------------
# Schema Info Route
# -------------------------

@router.get("/docs")
def docs_placeholder():
    return {"info": "Schema docs available at /docs/schema"}

@router.get("/docs/schema")
def get_schema():
    return {
        "tables": [
            {
                "table": "teams",
                "fields": ["id", "name"],
                "description": "Contains all football team names"
            },
            {
                "table": "players",
                "fields": [
                    "id", "name", "age", "nationality", "position",
                    "appearances", "minutes", "goals", "assists",
                    "yellow_cards", "red_cards", "shots_per_game",
                    "pass_success", "aerials_won", "motm", "rating",
                    "team_id"
                ],
                "description": "Player stats and relationship to their team"
            }
        ]
    }

# -------------------------
# Phase 2a.6 – Insight Cards Dummy
# -------------------------

@router.get("/insights")
def get_insight_cards(request: Request):
    tz_str = request.headers.get("X-Timezone", "UTC")
    now = format_timestamp(tz_str)

    dummy_insights = [
        {
            "card_id": str(uuid.uuid4()),
            "player_id": i,
            "match_scope": scope,
            "confidence": conf,
            "evidence": evidence,
            "recommendation": reco,
            "model_version": "v1.0-dummy",
            "generated_at": now,
            "i18n_key": key
        }
        for i, (scope, conf, evidence, reco, key) in enumerate([
            ("Season", 0.85, ["High pass accuracy", "Above average interceptions"], "Consider a tactical shift in midfield.", "insight_tactical_misfit"),
            ("Match", 0.72, ["Improved goal conversion"], "Player trending up; increase usage.", "insight_trending_up"),
            ("Competition", 0.65, ["Low match time", "High performance metrics when played"], "Underused asset; consider more playing time.", "insight_underused_asset"),
            ("Season", 0.70, ["Shift in role over recent matches"], "Role drift detected; review player positioning.", "insight_role_drift"),
            ("Match", 0.40, ["Abnormal biometrics recorded", "Recent injury history"], "Risk alert: Monitor player load and fitness.", "insight_risk_alert"),
        ], start=1)
    ]

    return JSONResponse(content={"insights": dummy_insights})

# -------------------------
# Phase 2a.7 – Feedback Logging
# -------------------------

@router.post("/feedback")
async def log_feedback(request: Request):
    body = await request.json()
    tz_str = request.headers.get("X-Timezone", "UTC")
    timestamp = format_timestamp(tz_str)
    db = SessionLocal()

    try:
        feedback = FeedbackLog(
            user_id=body.get("user_id", "anon"),
            request_id=body.get("request_id", str(uuid.uuid4())),
            session_id=body.get("session_id", "session_xyz"),
            card_id=body.get("card_id", "test-card-id"),
            action=body.get("action", "thumbs_up"),
            model_version=body.get("model_version", "v1.0-dummy"),
            timestamp=timestamp
        )
        db.add(feedback)
        db.commit()
        return {"status": "✅ feedback logged"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        db.close()

# -------------------------
# Phase 2a.8 – Metrics Reporting
# -------------------------

@router.get("/metrics")
def get_metrics(request: Request):
    tz_str = request.headers.get("X-Timezone", "UTC")
    db = SessionLocal()

    try:
        player_count = db.query(Player).count()
        team_count = db.query(Team).count()
        feedback_count = db.query(FeedbackLog).count()
        latest_feedback = db.query(FeedbackLog).order_by(FeedbackLog.timestamp.desc()).first()

        metrics = {
            "players": player_count,
            "teams": team_count,
            "feedback_logs": feedback_count,
            "latest_feedback_time": format_timestamp(tz_str, latest_feedback.timestamp) if latest_feedback else None
        }

        return JSONResponse(content={"metrics": metrics})
    finally:
        db.close()

# -------------------------
# Phase 2a.9 – Contract Projection Widget
# -------------------------

@router.get("/contracts/{player_id}")
def get_contract_projection(player_id: int, request: Request):
    tz_str = request.headers.get("X-Timezone", "UTC")
    db = SessionLocal()
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        db.close()
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        contract_data = {
            "player_id": player.id,
            "market_value": round(uniform(5.0, 120.0), 2),
            "contract_length_years": randint(1, 5),
            "renewal_risk_score": round(uniform(0.1, 1.0), 2),
            "confidence": round(uniform(0.5, 0.99), 2),
            "model_version": "v1.0-dummy",
            "generated_at": format_timestamp(tz_str),
            "i18n_key": "contract_projection_summary"
        }
        return contract_data
    finally:
        db.close()

# -------------------------
# Phase 2b.1 – Trending Players
# -------------------------

@router.get("/players/trending")
def get_trending_players_endpoint(request: Request):
    tz_str = request.headers.get("X-Timezone", "UTC")
    db = SessionLocal()

    try:
        top_players = get_trending_players(db, tz_str)
        # Convert Decimals to floats
        for player in top_players:
            for k, v in player.items():
                if isinstance(v, Decimal):
                    player[k] = float(v)
        return JSONResponse(content={"trending": top_players})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        db.close()

# -------------------------
# Phase 2b.2 – Chat-Based Search Logging
# -------------------------

@router.post("/chat/search")
async def chat_search(request: Request):
    body = await request.json()
    tz_str = request.headers.get("X-Timezone", "UTC")
    timestamp = format_timestamp(tz_str)
    db = SessionLocal()

    question = body.get("question", "")
    user_id = body.get("user_id", "anon")

    dummy_responses = {
        "defender": ["Achraf Hakimi", "Marquinhos"],
        "goalkeeper": ["Gianluigi Donnarumma"],
        "midfielder": ["Vitinha", "Fabián Ruiz"]
    }

    matched_players = []
    for keyword, names in dummy_responses.items():
        if keyword in question.lower():
            matched_players.extend(names)

    response_text = f"Found {len(matched_players)} players: {', '.join(matched_players)}"

    try:
        search_log = SearchLog(
            user_id=user_id,
            question=question,
            response=response_text,
            matched_players=len(matched_players),
            model_version="v1.0-dummy",
            timestamp=timestamp,
        )
        db.add(search_log)
        db.commit()
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        db.close()

    return {
        "question": question,
        "matched": matched_players,
        "response": response_text,
        "timestamp": timestamp,
    }

# -------------------------
# Phase 2b.3 – Chat Prompt Logging
# -------------------------

@router.post("/chat/prompt")
async def chat_prompt_log(request: Request):
    db = SessionLocal()
    body = await request.json()
    tz_str = request.headers.get("X-Timezone", "UTC")
    timestamp = format_timestamp(tz_str)

    user_id = body.get("user_id", "anon")
    prompt = body.get("prompt", "")
    response = f"🤖 AI says: Based on '{prompt}', here's some tactical insight..."
    
    log = ChatPromptLog(
        user_id=user_id,
        prompt=prompt,
        response=response,
        model_version="v1.0-dummy",
        timestamp=timestamp
    )
    db.add(log)
    db.commit()
    db.close()

    return {
        "prompt": prompt,
        "response": response,
        "timestamp": timestamp
    }

# -------------------------
# Phase 2b.4 – Chat Insight Generation
# -------------------------

@router.post("/chat/insight")
async def chat_insight(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    context = body.get("context", "")
    db = SessionLocal()

    try:
        insight = generate_insight(prompt=prompt, context=context, db=db)
        return {"insight": insight}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        db.close()

# -------------------------
# Phase 2b.5
# -------------------------

@router.post("/chat/ask")
async def smart_chat_router(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    tz_str = request.headers.get("X-Timezone", "UTC")
    db = SessionLocal()

    try:
        result = classify_prompt(prompt)

        if result["type"] == "insight":
            insight = generate_insight(prompt, "", db)
            return {"type": "insight", "insight": insight}

        elif result["type"] == "trending":
            from app.utils.trending import get_trending_players
            trending = get_trending_players(db, tz_str)
            return {"type": "trending", "players": trending}

        elif result["type"] == "contract":
            player = db.query(Player).filter(Player.name.ilike(f"%{result['player_name']}%")).first()
            if not player:
                return {"type": "contract", "error": f"Player '{result['player_name']}' not found"}
            # Reuse dummy logic
            from random import uniform, randint
            return {
                "type": "contract",
                "player_id": player.id,
                "market_value": round(uniform(5.0, 120.0), 2),
                "contract_length_years": randint(1, 5),
                "renewal_risk_score": round(uniform(0.1, 1.0), 2),
                "confidence": round(uniform(0.5, 0.99), 2),
                "model_version": "v1.0-dummy",
                "generated_at": format_timestamp(tz_str),
                "i18n_key": "contract_projection_summary"
            }
        
        elif result["type"] == "comparison":
            from app.services.player_comparator import compare_players
            comparison = compare_players(result["players"][0], result["players"][1], db)
            return {"type": "comparison", **comparison}

        return {"type": "unknown", "message": "Sorry, I couldn't understand the request."}

    finally:
        db.close()

# -------------------------
# Phase 2b.6
# -------------------------

@router.post("/chat/compare")
async def compare_endpoint(request: Request):
    body = await request.json()
    name1 = body.get("player1", "")
    name2 = body.get("player2", "")
    db = SessionLocal()

    try:
        result = compare_players(name1, name2, db)
        return result
    finally:
        db.close()

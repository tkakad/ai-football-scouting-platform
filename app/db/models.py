from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Date
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    players = relationship("Player", back_populates="team")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    nationality = Column(String)
    position = Column(String)
    appearances = Column(Integer)
    minutes = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    shots_per_game = Column(Float)
    pass_success = Column(Float)
    aerials_won = Column(Float)
    motm = Column(Integer)
    rating = Column(Float)
    team_id = Column(Integer, ForeignKey("teams.id"))
    
    team = relationship("Team", back_populates="players")
    status_intervals = relationship("StatusInterval", back_populates="player")
    biometric_data = relationship("FactBiometricMinute", back_populates="player")
    match_stats = relationship("MatchStat", back_populates="player")  # ✅ Added this line

class StatusInterval(Base):
    __tablename__ = "status_intervals"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    status_type = Column(String)
    status_description = Column(String)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    
    player = relationship("Player", back_populates="status_intervals")

class FactBiometricMinute(Base):
    __tablename__ = "fact_biometric_minute"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    sensor_id = Column(String)
    device_type = Column(String)
    consent_status = Column(Boolean)
    heart_rate_variability = Column(Float)
    sprint_count = Column(Integer)
    minutes_played = Column(Float)

    player = relationship("Player", back_populates="biometric_data")

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    request_id = Column(String)
    session_id = Column(String)
    action = Column(String)
    model_version = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class FeedbackLog(Base):
    __tablename__ = "feedback_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    request_id = Column(String)
    session_id = Column(String)
    card_id = Column(String)
    action = Column(String)
    model_version = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class SearchLog(Base):
    __tablename__ = "search_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    response = Column(Text)
    matched_players = Column(Integer)
    model_version = Column(String, default="v1.0-dummy")
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class ChatPromptLog(Base):
    __tablename__ = "chat_prompt_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_version = Column(String, default="v1.0-dummy")
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class MatchStat(Base):
    __tablename__ = "match_stats"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    match_date = Column(Date, nullable=False)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    pass_accuracy = Column(Float, default=0.0)

    player = relationship("Player", back_populates="match_stats")
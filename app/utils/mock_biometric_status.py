from datetime import datetime, timedelta
import random

from app.db.session import SessionLocal
from app.db.models import Player, StatusInterval, FactBiometricMinute

db = SessionLocal()

# Select a few players (you can limit or pick specific IDs)
players = db.query(Player).limit(5).all()

# --------------------------
# Insert into status_intervals
# --------------------------
for player in players:
    # Add a fake injury status
    injury = StatusInterval(
        player_id=player.id,
        status_type="injury",
        status_description="Hamstring strain",
        start_time=datetime.now() - timedelta(days=10),
        end_time=datetime.now() - timedelta(days=2),
    )
    db.add(injury)

    # Add a fake suspension
    suspension = StatusInterval(
        player_id=player.id,
        status_type="suspension",
        status_description="Red card ban",
        start_time=datetime.now() - timedelta(days=20),
        end_time=datetime.now() - timedelta(days=18),
    )
    db.add(suspension)

# --------------------------
# Insert into fact_biometric_minute
# --------------------------
for player in players:
    for i in range(5):  # 5 biometric entries per player
        data = FactBiometricMinute(
            player_id=player.id,
            timestamp=datetime.now() - timedelta(minutes=i * 5),
            sensor_id=f"HR-GPS-{player.id}",
            device_type="GPS",
            consent_status=True,
            heart_rate_variability=round(random.uniform(60, 100), 2),
            sprint_count=random.randint(5, 20),
            minutes_played=random.uniform(70, 90),
        )
        db.add(data)

db.commit()
db.close()

print("✅ Mock biometric + status data inserted successfully.")

import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3

np.random.seed(42)

N_USERS         = 5000
EVENTS_PER_USER = (20, 120)
OUTPUT_DIR      = Path("data/synthetic")
DB_PATH         = Path("data/churn.db")

EVENT_TYPES = [
    "app_open", "search", "play", "skip",
    "like", "share", "settings", "cancel_view"
]

EVENT_WEIGHTS_ACTIVE = [0.20, 0.18, 0.30, 0.10, 0.10, 0.05, 0.04, 0.03]
EVENT_WEIGHTS_ATRISK = [0.15, 0.10, 0.15, 0.20, 0.05, 0.03, 0.12, 0.20]

FEATURE_AREAS = ["discover", "library", "social", "account"]


def generate_sessions(user_id, is_churned, reg_date):
    weights = EVENT_WEIGHTS_ATRISK if is_churned else EVENT_WEIGHTS_ACTIVE
    n_events = np.random.randint(*EVENTS_PER_USER)
    if is_churned:
        n_events = int(n_events * 0.5)

    events = []
    current_time = reg_date + pd.Timedelta(days=np.random.randint(0, 30))
    session_id = None

    for i in range(n_events):
        if i % 8 == 0:
            session_id = f"{user_id}_s{i}"
            event_type = "app_open"
            duration = np.random.randint(60, 1800)
        else:
            event_type = np.random.choice(EVENT_TYPES, p=weights)
            duration = None

        events.append({
            "event_id":              f"{user_id}_e{i}",
            "user_id":               user_id,
            "session_id":            session_id,
            "event_type":            event_type,
            "feature_area":          np.random.choice(FEATURE_AREAS),
            "event_timestamp":       current_time,
            "session_duration_secs": duration
        })

        current_time += pd.Timedelta(seconds=np.random.randint(5, 300))

    return events


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating events for {N_USERS} users...")
    user_ids    = [f"u_{i:05d}" for i in range(N_USERS)]
    churn_flags = np.random.choice([True, False], size=N_USERS, p=[0.3, 0.7])
    reg_dates   = pd.date_range("2023-01-01", periods=N_USERS, freq="2h")

    all_events = []
    for uid, churned, reg in zip(user_ids, churn_flags, reg_dates):
        all_events.extend(generate_sessions(uid, churned, reg))

    df = pd.DataFrame(all_events)
    print(f"Generated {len(df):,} events")

    out_path = OUTPUT_DIR / "session_events.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved parquet to {out_path}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    df.to_sql("session_events", conn, if_exists="replace", index=False)

    users_df = pd.DataFrame({
        "user_id":           user_ids,
        "registration_date": reg_dates,
        "is_churned":        churn_flags,
        "registered_via":    np.random.choice([3, 4, 7], size=N_USERS, p=[0.4, 0.45, 0.15]),
        "city":              np.random.randint(1, 20, size=N_USERS),
        "plan_price":        np.random.choice([149, 199, 299], size=N_USERS, p=[0.5, 0.3, 0.2])
    })
    users_df.to_sql("users", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Written to SQLite at {DB_PATH}")
    print(f"\nChurn distribution: {churn_flags.sum()} churned / {(~churn_flags).sum()} retained")
    print("\nUsers preview:")
    print(users_df.head(3))
    print("\nEvents preview:")
    print(df.head(3))


if __name__ == "__main__":
    main()
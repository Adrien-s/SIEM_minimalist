import sqlite3
from datetime import datetime
from datetime import timedelta

def evaluate_rules(conn: sqlite3.Connection) -> None:
    """
    Pour chaque règle, compte le nombre d'événements matching dans la fenêtre,
    et logue si on dépasse le seuil.
    """
    now = datetime.now()

    # Récupère toutes les règles existantes
    cur = conn.execute(
        "SELECT id, channel, event_id, threshold, window_min FROM rules"
    )
    rules = cur.fetchall()
    print(f"[RULES] {len(rules)} règles à évaluer")

    for rule_id, channel, event_id, threshold, window_min in rules:
        # calcul de la fenêtre
        window_start = now - timedelta(minutes=window_min)
        start_str = window_start.isoformat()
        end_str   = now.isoformat()

        # compte des événements
        cur2 = conn.execute(
            """
            SELECT COUNT(*) FROM logs
            WHERE channel=? 
            AND event_id=? 
            AND time BETWEEN ? AND ?
            """,
            (channel, event_id, start_str, end_str)
        )
        count = cur2.fetchone()[0]

        # debug print
        print(f"[DEBUG] Rule#{rule_id} ({channel}#{event_id}) → window {start_str} → {end_str}, "
            f"threshold={threshold}, found={count}")

        if count >= threshold:
            print(f"[ALERTE] Rule#{rule_id}: {count}× {channel}#{event_id} en {window_min}min")
            conn.execute(
                "INSERT INTO alerts(rule_id, triggered_at, count) VALUES (?,?,?)",
                (rule_id, now.isoformat(), count)
            )
            # mise à jour du dernier check
        conn.execute(
            "UPDATE rules SET last_checked=? WHERE id=?",
            (now.isoformat(), rule_id)
        )

    conn.commit()
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
        rows = conn.execute(
            "SELECT time FROM logs WHERE channel=? AND event_id=?",
            (channel, event_id)
        ).fetchall()

        # puis on compte en Python en gérant le isoformat() local/UTC
        count = 0
        for (tstr,) in rows:
            try:
                ts = datetime.fromisoformat(tstr)
            except ValueError:
                # si jamais le format n'est pas ISO
                continue
            if window_start <= ts <= now:
                count += 1

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
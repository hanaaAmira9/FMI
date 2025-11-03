import hashlib
import os
import time
from plyer import notification
from core.gestion_db import *
from datetime import datetime
import threading

CHECK_INTERVAL = 10  # secondes
running = False
_db_lock = threading.Lock()
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "log.txt")

def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def notify_user(title, msg):
    try:
        notification.notify(title=title, message=msg, timeout=5)
    except:
        pass

def log_to_file(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")

def build_baseline_for_folder(folder):
    """Analyse un dossier et enregistre son état dans la base SQLite."""
    insert_folder(folder)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM folders WHERE path=?", (folder,))
    folder_id = c.fetchone()[0]
    conn.close()

    count = 0
    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            h = get_file_hash(path)
            if h:
                st = os.stat(path)
                insert_baseline_entry(
                    folder_id,
                    path,
                    h,
                    st.st_size,
                    datetime.fromtimestamp(st.st_mtime).isoformat()
                )
                count += 1

    notify_user("Baseline créée", f"{count} fichiers ajoutés depuis {folder}")
    log_event("baseline", f"Baseline créée pour {folder} ({count} fichiers)")
    log_to_file(f"Baseline créée pour {folder} ({count} fichiers)")

# ==============================
# INTÉGRITÉ
def check_integrity():
    """
    Vérifie l'intégrité des fichiers :
      1. Compare avec la baseline
      2. Compare avec les suspects existants
      3. Détecte et met à jour seulement les nouveaux changements
    """
    baseline_map = get_baseline()       # {path: hash}
    suspect_map = get_suspects_map()    # {path: last_hash}
    ok_count = mod_count = del_count = 0
    new_alerts = []
    file_status = []

    for path, expected_hash in baseline_map.items():
        current_hash = get_file_hash(path)

        # 🔸 Fichier supprimé
        if current_hash is None:
            if path not in suspect_map or suspect_map[path] is not None:
                upsert_suspect(path, expected_hash, None, "deleted")
                del_count += 1
                new_alerts.append((path, "deleted"))
                msg = f"Le  fichier : {path} a ete deleted."
                notify_user("Alerte FIM  ", msg)
                log_event("delete", f"Fichier supprimé: {path}")
            file_status.append((path, "❌ Supprimé"))
            continue

        # 🔸 Fichier déjà suspect
        if path in suspect_map:
            last_hash = suspect_map[path]

            # Hash différent → encore modifié → update suspect
            if last_hash != current_hash:
                upsert_suspect(path, expected_hash, current_hash, "modified")
                mod_count += 1
                new_alerts.append((path, "modified"))
                msg = f"Le  fichier : {path} a ete modifiés."
                notify_user("Alerte FIM  ",msg )
                log_to_file(msg)
                log_event("modification", f"Changement détecté dans suspect: {path}")
            else:
                # Hash identique → rien de nouveau
                file_status.append((path, "⚠️ Toujours suspect"))
            continue

        # 🔸 Fichier non suspect → comparaison baseline
        if current_hash == expected_hash:
            remove_suspect(path)
            ok_count += 1
            file_status.append((path, "✅ OK"))
        else:
            # Hash différent → première fois suspect
            upsert_suspect(path, expected_hash, current_hash, "modified")
            mod_count += 1
            new_alerts.append((path, "modified"))
            msg = f"Le  fichier : {path} a ete modifiés."
            notify_user("Alerte FIM  ", msg)
            log_to_file(msg)
            file_status.append((path, "⚠️ Modifié"))
            log_event("modification", f"Nouveau fichier modifié: {path}")

    # 🔸 Vérifier les fichiers dans suspects qui ont disparu de la baseline
    for path in suspect_map.keys():
        if path not in baseline_map:
            upsert_suspect(path, None, suspect_map[path], "deleted")
            del_count += 1
            new_alerts.append((path, "deleted"))
            msg = f"Le  fichier : {path} a ete deleted."
            notify_user("Alerte FIM  ", msg)
            log_to_file(msg)
            file_status.append((path, "❌ Supprimé (non dans baseline)"))
            log_event("delete", f"Fichier supprimé hors baseline: {path}")

    log_event("info", f"OK={ok_count}, Modifiés={mod_count}, Supprimés={del_count}")
    return ok_count, mod_count, del_count, file_status, new_alerts

def _monitor_loop():
    """Runs periodic integrity checks and sends alerts only for *new* suspects."""
    global running
    while running:
        try:
            ok, mod, sup, _, new_alerts = check_integrity()

            # 🔹 Send notification only if new suspects appeared
            if new_alerts:
                mod_new = sum(1 for _, s in new_alerts if s == "modified")
                del_new = sum(1 for _, s in new_alerts if s == "deleted")

                msg = f"Nouveaux fichiers suspects: {mod_new} modifiés, {del_new} supprimés."

                log_to_file(f"[ALERTE] {msg}")

        except Exception as e:
            log_to_file(f"Erreur dans monitor_loop: {e}")

        time.sleep(CHECK_INTERVAL)

def start_monitoring():
    global running, _monitor_thread
    if running:
        return None
    running = True
    _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    _monitor_thread.start()
    return _monitor_thread

def stop_monitoring():
    global running
    running = False
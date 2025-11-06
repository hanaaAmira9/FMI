import json
import os
import hashlib
from core.email_sender import send_confirmation_email  # ton module existant

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # <- dossier principal (celui contenant main.py)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CURRENT_USER_FILE = os.path.join(BASE_DIR, "userCurrent.json")

USER_ACTUEL = ""


# ========= 🔹 Fonctions utilitaires =========
def hash_password(password: str) -> str:
    """Retourne le hash SHA256 du mot de passe."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Charge les utilisateurs depuis le fichier JSON."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    """Sauvegarde le dictionnaire d'utilisateurs dans users.json."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def save_current_user(username):
    """Sauvegarde le user actuellement connecté dans user.json."""
    with open(CURRENT_USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f, indent=4)


def load_current_user():
    """Retourne l'utilisateur actuellement connecté."""
    if os.path.exists(CURRENT_USER_FILE):
        with open(CURRENT_USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("username", "")
    return USER_ACTUEL


# ========= 🔸 Fonctions principales =========
def register_user(username, email, password):
    """Crée un nouvel utilisateur avec mot de passe hashé."""
    users = load_users()

    if email in users:
        return False, "❌ Cet email est déjà enregistré."

    users[email] = {
        "username": username,
        "password": hash_password(password)
    }

    save_users(users)
    send_confirmation_email(email, username)
    return True, "✅ Compte créé avec succès !"


def verify_login(email, password):
    """Vérifie si l'utilisateur existe et si le mot de passe est correct."""
    global USER_ACTUEL  # ⚠️ indispensable

    users = load_users()

    if email not in users:
        return False, "❌ Aucun compte trouvé avec cet email."

    hashed_input = hash_password(password)
    if users[email]["password"] == hashed_input:
        USER_ACTUEL = users[email]['username']
        save_current_user(USER_ACTUEL)
        return True, f"✅ Bienvenue {USER_ACTUEL} !"
    else:
        return False, "❌ Mot de passe incorrect."


def reset_password(email, new_password):
    """Réinitialise le mot de passe d'un utilisateur existant."""
    users = load_users()

    if email not in users:
        return False, "❌ Aucun compte trouvé avec cet email."

    users[email]["password"] = hash_password(new_password)
    save_users(users)

    send_confirmation_email(email, users[email]["username"])
    return True, "✅ Mot de passe réinitialisé avec succès !"


def list_users():
    """Affiche et retourne la liste des utilisateurs et leurs rôles."""
    users = load_users()
    if not users:
        return []

    current_user = load_current_user()
    user_list = []

    for email, data in users.items():
        role = "Admin" if data['username'] == current_user else "User standard"

        user_list.append({
            "username": data["username"],
            "role": role
        })

    return user_list


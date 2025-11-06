import json
import os
import hashlib
from core.email_sender import send_confirmation_email  # ton module existant

# === Constantes ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CURRENT_USER_FILE = os.path.join(BASE_DIR, "userCurrent.json")
USER_ACTUEL = ""


# === Fonctions utilitaires ===
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


# === 🔸 Fonctions principales ===

def register_user(username, email, password):
    """Crée un nouvel utilisateur avec mot de passe hashé.
    Vérifie l’unicité de l’email et du username.
    """
    users = load_users()

    # Vérif email existant
    if email in users:
        return False, "Cet email est déjà enregistré."

    # Vérif username déjà pris
    for user_data in users.values():
        if user_data["username"].lower() == username.lower():
            return False, "Ce nom d'utilisateur est déjà pris."

    # Enregistrement
    users[email] = {
        "username": username,
        "password": hash_password(password)
    }

    save_users(users)
    send_confirmation_email(email, username)
    return True, "Compte créé avec succès !"


def verify_login(email, password):
    """Vérifie si l'utilisateur existe et si le mot de passe est correct."""
    global USER_ACTUEL

    users = load_users()
    if email not in users:
        return False, "Aucun compte trouvé avec cet email."

    hashed_input = hash_password(password)
    if users[email]["password"] == hashed_input:
        USER_ACTUEL = users[email]["username"]
        save_current_user(USER_ACTUEL)
        return True, f"Bienvenue {USER_ACTUEL} !"
    else:
        return False, "Mot de passe incorrect."


def reset_password(email, new_password):
    """Réinitialise le mot de passe d'un utilisateur existant."""
    users = load_users()
    if email not in users:
        return False, "Aucun compte trouvé avec cet email."

    users[email]["password"] = hash_password(new_password)
    save_users(users)
    send_confirmation_email(email, users[email]["username"])
    return True, "Mot de passe réinitialisé avec succès !"


def list_users():
    """Retourne la liste des utilisateurs et leurs rôles."""
    users = load_users()
    if not users:
        return []
    current_user = load_current_user()
    user_list = []
    for email, data in users.items():
        role = "Admin" if data["username"] == current_user else "User standard"
        user_list.append({
            "username": data["username"],
            "email": email,
            "role": role
        })
    return user_list




def change_username(email, new_username):
    """Permet de changer le nom d'utilisateur associé à un email."""
    users = load_users()
    if email not in users:
        return False, "Utilisateur non trouvé."

    # Vérifier que le nouveau nom n'est pas déjà utilisé
    for data in users.values():
        if data["username"].lower() == new_username.lower():
            return False, "Ce nom d'utilisateur est déjà pris."

    users[email]["username"] = new_username
    save_users(users)
    send_confirmation_email(email, new_username)
    return True, "Nom d'utilisateur changé avec succès."


def change_email(old_email, new_email):
    """Change l'email d’un utilisateur."""
    users = load_users()

    if old_email not in users:
        return False, "Ancien email introuvable."
    if new_email in users:
        return False, "Le nouvel email est déjà enregistré."

    users[new_email] = users.pop(old_email)
    save_users(users)
    send_confirmation_email(new_email, users[new_email]["username"])
    return True, "Email modifié avec succès."


def change_password(email, old_password, new_password):
    """Change le mot de passe si l’ancien est correct."""
    users = load_users()

    if email not in users:
        return False, "Utilisateur non trouvé."

    hashed_old = hash_password(old_password)
    if users[email]["password"] != hashed_old:
        return False, "Ancien mot de passe incorrect."

    users[email]["password"] = hash_password(new_password)
    save_users(users)
    return True, "Mot de passe changé avec succès."

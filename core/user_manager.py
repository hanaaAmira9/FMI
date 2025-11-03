import json
import os
import hashlib
from core.email_sender import send_confirmation_email  # ton module existant

USERS_FILE = "users.json"


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
    users = load_users()

    if email not in users:
        return False, "❌ Aucun compte trouvé avec cet email."

    hashed_input = hash_password(password)
    if users[email]["password"] == hashed_input:
        print(hashed_input)
        return True, f"✅ Bienvenue {users[email]['username']} !"
    else:
        return False, "❌ Mot de passe incorrect."


def reset_password(email, new_password):
    """Réinitialise le mot de passe d'un utilisateur existant."""
    users = load_users()

    if email not in users:
        return False, "❌ Aucun compte trouvé avec cet email."

    users[email]["password"] = hash_password(new_password)
    save_users(users)

    # Optionnel : notifier l'utilisateur par email
    send_confirmation_email(email, users[email]["username"])
    return True, "✅ Mot de passe réinitialisé avec succès !"

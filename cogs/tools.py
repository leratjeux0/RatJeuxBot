import json

def get_Bank(user_id):
    """Récupère le solde d'un utilisateur."""
    bank = load_data("Money")
    
    if user_id not in bank:
        create_user(user_id)

    return bank.get(str(user_id), 100)


def update_Bank(user_id, amount):
    """Met à jour le solde d'un utilisateur."""
    bank = load_data("Money")

    if user_id not in bank:
        create_user(user_id)

    bank[str(user_id)] = bank.get(str(user_id), 100) + amount
    save_data("Money",bank)

def create_user(user_id):
    bank = load_data("Money")

    if str(user_id) not in bank:
        bank[str(user_id)] = 100
        save_data("Money", bank) 

# --- --- ---

def load_data(filename):
    with open(f"./json/{filename}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_data(filename, data={}):
    with open(f"./json/{filename}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    
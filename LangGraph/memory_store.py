MEMORY_DB = {}

def save_user_memory(user_id, memory):

    MEMORY_DB[user_id] = memory

def load_user_memory(user_id):

    return MEMORY_DB.get(
        user_id,
        "No previous preference found"
    )
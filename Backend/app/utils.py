
def user_helper(user) -> dict:
    return {
        "_id": str(user["_id"]),
        "username": user.get("username", user.get("name", "")),  # Support both "username" and "name"
        "email": user["email"],
    }

def message_helper(message) -> dict:
    return {
        "_id": str(message["_id"]),
        "history_id": str(message.get("history_id", "")),
        "role": message.get("role", ""),
        "content": message.get("content", ""),
        "timestamp": message.get("timestamp", None),
    }

def history_helper(history) -> dict:
    return {
        "_id": str(history["_id"]),
        "user_id": str(history.get("user_id", "")),
        "created_at": history.get("created_at", None),
    }

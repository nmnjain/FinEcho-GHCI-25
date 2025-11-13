from sqlalchemy.orm import Session
from . import models
import json

# For this prototype, we'll hardcode the user's ID.
FIXED_USER_ID = 1 # This corresponds to "Nisha"

def save_voice_embedding(db: Session, embedding):
    user = db.query(models.User).filter(models.User.id == FIXED_USER_ID).first()
    if user:
        # Convert numpy array to a list, then to a JSON string for storage
        user.voice_embedding = json.dumps(embedding.tolist())
        db.commit()
        return True
    return False

def get_user_voice_embedding(db: Session):
    user = db.query(models.User).filter(models.User.id == FIXED_USER_ID).first()
    return user.voice_embedding if user else None

def get_balance(db: Session, account_type: str):
    account = db.query(models.Account).filter(
        models.Account.owner_id == FIXED_USER_ID,
        models.Account.account_type == account_type
    ).first()
    return account.balance if account else None

def execute_transfer(db: Session, amount: float, recipient_name: str, from_account_type: str = "savings"):
    sender_account = db.query(models.Account).filter(
        models.Account.owner_id == FIXED_USER_ID,
        models.Account.account_type == from_account_type
    ).first()

    if not sender_account:
        return {"success": False, "message": f"You do not have a {from_account_type} account."}
    
    if sender_account.balance < amount:
        return {"success": False, "message": "You have insufficient funds for this transfer."}

    recipient_user = db.query(models.User).filter(models.User.username == recipient_name).first()
    if not recipient_user:
        return {"success": False, "message": f"Could not find a user named {recipient_name}."}
        
    recipient_account = db.query(models.Account).filter(
        models.Account.owner_id == recipient_user.id,
        models.Account.account_type == "savings"
    ).first()

    if not recipient_account:
        return {"success": False, "message": f"{recipient_name} does not have a savings account to receive funds."}
    
    try:
        sender_account.balance -= amount
        recipient_account.balance += amount
        db.commit()
        return {"success": True, "message": f"Successfully transferred {amount} to {recipient_name}."}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"An error occurred during the transaction: {e}"}
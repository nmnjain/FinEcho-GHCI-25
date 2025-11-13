import spacy
import re
from sqlalchemy.orm import Session
from . import crud

nlp = spacy.load("en_core_web_sm")

INTENT_SLOTS = {
    "transfer_money": ["amount", "recipient"],
    "check_balance": ["account_type"],
}

def extract_entities(text: str):
    # ... (this function remains the same as in Phase 4)
    doc = nlp(text.lower())
    entities = {}
    amount_match = re.search(r'(\d[\d,]*\.?\d*)\s*(rupees|dollars|rs)', text.lower())
    if amount_match:
        entities["amount"] = float(amount_match.group(1).replace(",", ""))
    if "recipient" not in entities:
        match = re.search(r"to\s+([a-z]+)", text.lower())
        if match:
            entities["recipient"] = match.group(1).title()
    if "savings" in text.lower():
        entities["account_type"] = "savings"
    elif "checking" in text.lower() or "current" in text.lower():
        entities["account_type"] = "checking"
    return entities

def get_dialogue_response(session_state: dict, transcribed_text: str, db: Session):
    if not session_state.get("intent"):
        if "balance" in transcribed_text.lower():
            session_state["intent"] = "check_balance"
        elif "transfer" in transcribed_text.lower() or "send" in transcribed_text.lower():
            session_state["intent"] = "transfer_money"
        else:
            return "I don't understand that command.", session_state, False
        session_state["filled_slots"] = {}

    entities = extract_entities(transcribed_text)
    session_state["filled_slots"].update(entities)
    
    intent = session_state.get("intent")
    filled_slots = session_state.get("filled_slots", {})
    
    # This is a flag we will return to the main API
    requires_verification = False

    if intent == "transfer_money" and session_state.get("awaiting_verification"):
        # This case is handled by the /verify endpoint now
        response_text = "Verification is being processed."
        return response_text, session_state, False

    missing_slots = [slot for slot in INTENT_SLOTS.get(intent, []) if slot not in filled_slots]

    if not missing_slots:
        response_text = "Something went wrong."
        if intent == "check_balance":
            balance = crud.get_balance(db, filled_slots["account_type"])
            response_text = f"The balance in your {filled_slots['account_type']} account is {balance:.2f} rupees." if balance is not None else f"I couldn't find your {filled_slots['account_type']} account."
            session_state = {}
        
        elif intent == "transfer_money":
            # Instead of executing, we now trigger verification
            amount = filled_slots.get('amount')
            recipient = filled_slots.get('recipient')
            response_text = f"To transfer {amount} to {recipient}, please say: 'My voice is my password'."
            session_state["awaiting_verification"] = True # Set the new state
            requires_verification = True
        
    else:
        next_slot_to_ask = missing_slots[0]
        if next_slot_to_ask == "amount":
            response_text = "How much would you like to transfer?"
        elif next_slot_to_ask == "recipient":
            response_text = "Who is the recipient?"
        elif next_slot_to_ask == "account_type":
            response_text = "For which account? Savings or checking?"
            
    return response_text, session_state, requires_verification
import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Define the slots required for each intent
INTENT_SLOTS = {
    "transfer_money": ["amount", "recipient"],
    "check_balance": [], 
    "view_history": []
}

def extract_entities(text: str):
    """Extracts entities from a given text."""
    doc = nlp(text.lower())
    entities = {}
    
    # spaCy's Named Entity Recognition (NER)
    for ent in doc.ents:
        if ent.label_ in ["MONEY", "CARDINAL"]:
            # Use regex to find the first number in the entity text
            amount_match = re.search(r'\d+\.?\d*', ent.text.replace(",", ""))
            if amount_match:
                entities["amount"] = float(amount_match.group(0))
        elif ent.label_ == "PERSON":
            # Assuming the first person found is the recipient
            if "recipient" not in entities:
                entities["recipient"] = ent.text.title()

    # Rule-based extraction if NER fails
    if "recipient" not in entities:
        # Look for "to [Name]" pattern
        match = re.search(r"to\s+([a-z]+)", text.lower())
        if match:
            entities["recipient"] = match.group(1).title()

    return entities

def get_dialogue_response(session_state: dict, transcribed_text: str):
    """
    Manages the conversation state and generates a response.
    """
    # If there's no active conversation, try to determine a new intent
    if not session_state.get("intent"):
        doc = nlp(transcribed_text.lower())
        if "balance" in transcribed_text.lower():
            session_state["intent"] = "check_balance"
        elif "transfer" in transcribed_text.lower() or "send" in transcribed_text.lower():
            session_state["intent"] = "transfer_money"
        elif "history" in transcribed_text.lower() or "transactions" in transcribed_text.lower():
            session_state["intent"] = "view_history"
        else:
            return "I'm sorry, I'm not sure how to help with that.", session_state

        # Initialize the slots for the new intent
        session_state["filled_slots"] = {}

    # Extract entities from the user's latest message
    entities = extract_entities(transcribed_text)
    # Fill any new slots
    for slot, value in entities.items():
        if slot not in session_state["filled_slots"]:
            session_state["filled_slots"][slot] = value

    # --- Dialogue Logic ---
    intent = session_state["intent"]
    required_slots = INTENT_SLOTS[intent]
    filled_slots = session_state["filled_slots"]
    
    # Check if all required slots for the intent are filled
    missing_slots = [slot for slot in required_slots if slot not in filled_slots]

    if not missing_slots:
        # --- All slots are filled, time to execute or confirm ---
        if intent == "check_balance":
            response_text = "Checking your account balance now."
        elif intent == "view_history":
            response_text = "Fetching your recent transactions."
        elif intent == "transfer_money":
            amount = filled_slots.get('amount')
            recipient = filled_slots.get('recipient')
            response_text = f"Okay, proceeding to transfer {amount} to {recipient}."
        
        # Clear the session state after completing the action
        session_state = {}
    else:
        # --- There are missing slots, ask for the next one ---
        next_slot_to_ask = missing_slots[0]
        if next_slot_to_ask == "amount":
            response_text = "How much would you like to send?"
        elif next_slot_to_ask == "recipient":
            response_text = "Who should I send the money to?"
    
    return response_text, session_state
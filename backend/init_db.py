from .database import SessionLocal, engine
from .models import Base, User, Account

# Create the tables in the database
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

# Create a new session
db = SessionLocal()

# --- Check if users already exist to prevent duplicates ---
if db.query(User).count() == 0:
    print("Populating database with mock data...")
    
    # Create mock users
    user1 = User(username="Naman")
    user2 = User(username="Iuc")
    
    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    
    # Create mock accounts
    account1 = Account(account_type="savings", balance=15000.75, owner_id=user1.id)
    account2 = Account(account_type="checking", balance=5230.50, owner_id=user1.id)
    account3 = Account(account_type="savings", balance=25000.00, owner_id=user2.id)
    
    db.add_all([account1, account2, account3])
    db.commit()
    
    print("Mock data added successfully.")
else:
    print("Database already populated.")

db.close()
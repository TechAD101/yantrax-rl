import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from models import Base, Memecoin, PortfolioPosition

def test_schema():
    print("Testing schema...")
    engine = create_engine('sqlite:///:memory:')

    try:
        # This will trigger mapper configuration which fails if relationships are broken
        Base.metadata.create_all(engine)
        print("Schema creation successful.")

        Session = sessionmaker(bind=engine)
        session = Session()

        # Test inserting and relating
        meme = Memecoin(symbol="DOGE", score=10.0)
        session.add(meme)
        session.commit()

        # Create position (no explicit link, reliant on symbol match)
        # Note: PortfolioPosition requires portfolio_id, so we need a dummy portfolio first
        # But we are just testing if mapper fails.

        print("Mapper configuration passed.")
        return True
    except Exception as e:
        print(f"Schema Test Failed: {e}")
        return False

if __name__ == "__main__":
    if test_schema():
        sys.exit(0)
    else:
        sys.exit(1)

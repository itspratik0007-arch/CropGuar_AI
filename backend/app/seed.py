import sys
import os

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.models import Plant
from app.seed_data import SEED_PLANTS

def seed_plants():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted_count = 0
        for data in SEED_PLANTS:
            existing = db.query(Plant).filter(
                (Plant.common_name == data["common_name"]) | 
                (Plant.scientific_name == data["scientific_name"])
            ).first()

            if not existing:
                plant = Plant(**data)
                db.add(plant)
                inserted_count += 1
            else:
                # Update details if existing record is curated_local
                for key, value in data.items():
                    setattr(existing, key, value)

        db.commit()
        print(f"Plantopedia seed completed successfully. Inserted: {inserted_count}, Total seed catalog: {len(SEED_PLANTS)}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding Plantopedia: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_plants()

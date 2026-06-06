import pytest
from backend.database import Database

@pytest.fixture
def db():
    database = Database(":memory:")
    database.initialize()
    yield database
    database.close()

def test_ensure_default_campaign_creates_one_record(db):
    # Call ensure_default_campaign twice on an empty database
    campaign1 = db.ensure_default_campaign()
    campaign2 = db.ensure_default_campaign()

    # Assert they are the same campaign
    assert campaign1["id"] == "campaign_1"
    assert campaign2["id"] == "campaign_1"

    # Verify that only one record exists in the campaigns table
    cursor = db.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE id = 'campaign_1'")
    count = cursor.fetchone()[0]

    assert count == 1, "Only one default campaign should be created even if called multiple times"

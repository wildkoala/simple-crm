"""Tests for opportunities CRUD, pipeline metrics, and filtering."""

from app.models.models import ContractVehicle, Opportunity
from app.utils import generate_id


def _make_vehicle(db, **overrides):
    defaults = {"id": generate_id(), "name": "Test Vehicle", "notes": ""}
    defaults.update(overrides)
    v = ContractVehicle(**defaults)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _make_opportunity(db, user_id, **overrides):
    defaults = {
        "id": generate_id(),
        "title": "Test Opportunity",
        "agency": "DoD",
        "stage": "identified",
        "notes": "",
        "capture_manager_id": user_id,
        "created_by_user_id": user_id,
    }
    defaults.update(overrides)
    opp = Opportunity(**defaults)
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp


# --- GET list ---


def test_get_opportunities_empty(client, admin_headers, admin_user):
    response = client.get("/opportunities", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_opportunities(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id)
    response = client.get("/opportunities", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_filter_stage(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, stage="identified")
    _make_opportunity(db, admin_user.id, title="Qualified Opp", stage="qualified")
    response = client.get("/opportunities?stage=qualified", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage"] == "qualified"


def test_get_opportunities_filter_agency(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, agency="DoD")
    _make_opportunity(db, admin_user.id, title="GSA Opp", agency="GSA")
    response = client.get("/opportunities?agency=GSA", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_filter_naics(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, naics_code="541512")
    response = client.get("/opportunities?naics_code=541512", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_filter_set_aside(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, set_aside_type="8a")
    response = client.get("/opportunities?set_aside_type=8a", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_filter_source(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, source="sam_gov")
    response = client.get("/opportunities?source=sam_gov", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_filter_value(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, estimated_value=5000000)
    _make_opportunity(db, admin_user.id, title="Big One", estimated_value=50000000)
    response = client.get(
        "/opportunities?min_value=10000000&max_value=100000000", headers=admin_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_opportunities_search(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, title="Zero Trust Architecture")
    _make_opportunity(db, admin_user.id, title="Cloud Migration")
    response = client.get("/opportunities?search=Zero", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- GET single ---


def test_get_opportunity_by_id(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    response = client.get(f"/opportunities/{opp.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Opportunity"


def test_get_opportunity_not_found(client, admin_headers, admin_user):
    response = client.get("/opportunities/nonexistent", headers=admin_headers)
    assert response.status_code == 404


# --- Pipeline metrics ---


def test_pipeline_metrics_empty(client, admin_headers, admin_user):
    response = client.get("/opportunities/pipeline", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_opportunities"] == 0
    assert data["pipeline_value"] == 0
    assert data["win_rate"] == 0


def test_pipeline_metrics_with_data(client, admin_headers, db, admin_user):
    _make_opportunity(db, admin_user.id, estimated_value=10000000, win_probability=50, stage="capture")
    _make_opportunity(db, admin_user.id, title="Won", estimated_value=5000000, win_probability=100, stage="awarded")
    _make_opportunity(db, admin_user.id, title="Lost", estimated_value=3000000, win_probability=0, stage="lost")
    response = client.get("/opportunities/pipeline", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_opportunities"] == 3
    assert data["pipeline_value"] == 18000000
    assert data["win_rate"] == 50.0  # 1 awarded / (1 awarded + 1 lost)
    assert data["average_deal_size"] == 6000000
    assert "capture" in data["by_stage"]
    assert "DoD" in data["by_agency"]


# --- POST ---


def test_create_opportunity(client, admin_headers, admin_user):
    response = client.post(
        "/opportunities",
        json={
            "title": "New Opp",
            "agency": "NASA",
            "stage": "identified",
            "naics_code": "541512",
            "set_aside_type": "small_business",
            "estimated_value": 12000000,
            "win_probability": 30,
            "notes": "Test",
            "vehicle_ids": [],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Opp"
    assert data["agency"] == "NASA"
    assert data["stage"] == "identified"


def test_create_opportunity_with_vehicle(client, admin_headers, db, admin_user):
    v = _make_vehicle(db, name="OASIS")
    response = client.post(
        "/opportunities",
        json={
            "title": "Vehicle Opp",
            "stage": "qualified",
            "notes": "",
            "vehicle_ids": [v.id],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert v.id in data["vehicle_ids"]


def test_create_opportunity_auto_proposal(client, admin_headers, admin_user):
    """Creating an opportunity at 'proposal' stage auto-creates a proposal."""
    response = client.post(
        "/opportunities",
        json={
            "title": "Proposal Stage Opp",
            "stage": "proposal",
            "notes": "",
            "vehicle_ids": [],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    opp_id = response.json()["id"]

    # Check proposal was created
    proposals = client.get(
        f"/proposals?opportunity_id={opp_id}", headers=admin_headers
    )
    assert proposals.status_code == 200
    assert len(proposals.json()) == 1


# --- PUT ---


def test_update_opportunity(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    response = client.put(
        f"/opportunities/{opp.id}",
        json={
            "title": "Updated Opp",
            "agency": "GSA",
            "stage": "qualified",
            "notes": "Updated",
            "vehicle_ids": [],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Opp"
    assert data["stage"] == "qualified"


def test_update_opportunity_not_found(client, admin_headers, admin_user):
    response = client.put(
        "/opportunities/nonexistent",
        json={"title": "X", "stage": "identified", "notes": "", "vehicle_ids": []},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_update_opportunity_creates_proposal_on_stage_change(client, admin_headers, db, admin_user):
    """Moving to proposal stage via PUT auto-creates a proposal."""
    opp = _make_opportunity(db, admin_user.id, stage="capture")
    response = client.put(
        f"/opportunities/{opp.id}",
        json={
            "title": opp.title,
            "stage": "proposal",
            "notes": "",
            "vehicle_ids": [],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200

    proposals = client.get(
        f"/proposals?opportunity_id={opp.id}", headers=admin_headers
    )
    assert len(proposals.json()) == 1


def test_update_opportunity_with_vehicles(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    v = _make_vehicle(db, name="MAS")
    response = client.put(
        f"/opportunities/{opp.id}",
        json={
            "title": opp.title,
            "stage": "identified",
            "notes": "",
            "vehicle_ids": [v.id],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert v.id in response.json()["vehicle_ids"]


# --- PATCH ---


def test_patch_opportunity(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    response = client.patch(
        f"/opportunities/{opp.id}",
        json={"title": "Patched Title"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Patched Title"


def test_patch_opportunity_not_found(client, admin_headers, admin_user):
    response = client.patch(
        "/opportunities/nonexistent",
        json={"title": "Ghost"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_patch_opportunity_vehicles(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    v = _make_vehicle(db, name="SeaPort")
    response = client.patch(
        f"/opportunities/{opp.id}",
        json={"vehicle_ids": [v.id]},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert v.id in response.json()["vehicle_ids"]


def test_patch_opportunity_auto_proposal(client, admin_headers, db, admin_user):
    """PATCH to proposal stage auto-creates a proposal."""
    opp = _make_opportunity(db, admin_user.id, stage="teaming")
    response = client.patch(
        f"/opportunities/{opp.id}",
        json={"stage": "proposal"},
        headers=admin_headers,
    )
    assert response.status_code == 200

    proposals = client.get(
        f"/proposals?opportunity_id={opp.id}", headers=admin_headers
    )
    assert len(proposals.json()) == 1


# --- DELETE ---


def test_delete_opportunity(client, admin_headers, db, admin_user):
    opp = _make_opportunity(db, admin_user.id)
    response = client.delete(f"/opportunities/{opp.id}", headers=admin_headers)
    assert response.status_code == 204

    response = client.get(f"/opportunities/{opp.id}", headers=admin_headers)
    assert response.status_code == 404


def test_delete_opportunity_not_found(client, admin_headers, admin_user):
    response = client.delete("/opportunities/nonexistent", headers=admin_headers)
    assert response.status_code == 404


# --- Model property ---


def test_vehicle_ids_property(db, admin_user):
    """Test Opportunity.vehicle_ids property."""
    v = _make_vehicle(db, name="OASIS")
    opp = Opportunity(
        id=generate_id(),
        title="Property Test",
        stage="identified",
        notes="",
        capture_manager_id=admin_user.id,
        created_by_user_id=admin_user.id,
    )
    opp.vehicles = [v]
    db.add(opp)
    db.commit()
    db.refresh(opp)
    assert opp.vehicle_ids == [v.id]

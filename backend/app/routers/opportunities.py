from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_active_user
from app.database import get_db
from app.models.models import ContractVehicle, Opportunity, Proposal, User
from app.schemas.schemas import (
    Opportunity as OpportunitySchema,
)
from app.schemas.schemas import (
    OpportunityCreate,
    OpportunityPatch,
    OpportunityUpdate,
    PipelineMetrics,
)
from app.utils import generate_id

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=List[OpportunitySchema])
def get_opportunities(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    stage: Optional[str] = Query(default=None),
    agency: Optional[str] = Query(default=None),
    naics_code: Optional[str] = Query(default=None),
    set_aside_type: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    min_value: Optional[float] = Query(default=None),
    max_value: Optional[float] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Opportunity).options(selectinload(Opportunity.vehicles))

    if stage:
        query = query.filter(Opportunity.stage == stage)
    if agency:
        query = query.filter(Opportunity.agency.ilike(f"%{agency}%"))
    if naics_code:
        query = query.filter(Opportunity.naics_code == naics_code)
    if set_aside_type:
        query = query.filter(Opportunity.set_aside_type == set_aside_type)
    if source:
        query = query.filter(Opportunity.source == source)
    if min_value is not None:
        query = query.filter(Opportunity.estimated_value >= min_value)
    if max_value is not None:
        query = query.filter(Opportunity.estimated_value <= max_value)
    if search:
        query = query.filter(
            Opportunity.title.ilike(f"%{search}%")
            | Opportunity.solicitation_number.ilike(f"%{search}%")
            | Opportunity.agency.ilike(f"%{search}%")
        )

    return query.order_by(Opportunity.updated_at.desc()).offset(skip).limit(limit).all()


@router.get("/pipeline", response_model=PipelineMetrics)
def get_pipeline_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opportunities = db.query(Opportunity).all()
    total = len(opportunities)
    pipeline_value = sum(o.estimated_value or 0 for o in opportunities)

    # Expected revenue weighted by win probability
    expected_revenue = sum(
        (o.estimated_value or 0) * (o.win_probability or 0) / 100 for o in opportunities
    )

    # Win rate: awarded / (awarded + lost)
    awarded = sum(1 for o in opportunities if o.stage == "awarded")
    lost = sum(1 for o in opportunities if o.stage == "lost")
    win_rate = (awarded / (awarded + lost) * 100) if (awarded + lost) > 0 else 0

    # Average deal size
    valued = [o for o in opportunities if o.estimated_value and o.estimated_value > 0]
    avg_deal = sum(o.estimated_value for o in valued) / len(valued) if valued else 0

    # By stage
    by_stage = {}
    for o in opportunities:
        stage = o.stage
        if stage not in by_stage:
            by_stage[stage] = {"count": 0, "value": 0}
        by_stage[stage]["count"] += 1
        by_stage[stage]["value"] += o.estimated_value or 0

    # By agency
    by_agency = {}
    for o in opportunities:
        agency = o.agency or "Unknown"
        if agency not in by_agency:
            by_agency[agency] = {"count": 0, "value": 0}
        by_agency[agency]["count"] += 1
        by_agency[agency]["value"] += o.estimated_value or 0

    return PipelineMetrics(
        total_opportunities=total,
        pipeline_value=pipeline_value,
        expected_award_revenue=expected_revenue,
        win_rate=round(win_rate, 1),
        average_deal_size=round(avg_deal, 2),
        by_stage=by_stage,
        by_agency=by_agency,
    )


@router.get("/{opportunity_id}", response_model=OpportunitySchema)
def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opportunity = (
        db.query(Opportunity)
        .options(selectinload(Opportunity.vehicles))
        .filter(Opportunity.id == opportunity_id)
        .first()
    )
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )
    return opportunity


def _resolve_vehicles(vehicle_ids: List[str], db: Session) -> list:
    if not vehicle_ids:
        return []
    return db.query(ContractVehicle).filter(ContractVehicle.id.in_(vehicle_ids)).all()


@router.post("", response_model=OpportunitySchema, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opp: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    new_opp = Opportunity(
        id=generate_id(),
        title=opp.title,
        agency=opp.agency,
        account_id=opp.account_id,
        naics_code=opp.naics_code,
        set_aside_type=opp.set_aside_type,
        estimated_value=opp.estimated_value,
        solicitation_number=opp.solicitation_number,
        source=opp.source,
        stage=opp.stage,
        capture_manager_id=opp.capture_manager_id or current_user.id,
        expected_release_date=opp.expected_release_date,
        proposal_due_date=opp.proposal_due_date,
        award_date_estimate=opp.award_date_estimate,
        win_probability=opp.win_probability,
        notes=opp.notes,
        created_by_user_id=current_user.id,
    )

    new_opp.vehicles = _resolve_vehicles(opp.vehicle_ids, db)

    # Auto-create proposal when stage is "proposal"
    if opp.stage == "proposal":
        proposal = Proposal(
            id=generate_id(),
            opportunity_id=new_opp.id,
            proposal_manager_id=current_user.id,
            status="not_started",
            submission_deadline=opp.proposal_due_date,
        )
        db.add(proposal)

    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)
    return new_opp


@router.put("/{opportunity_id}", response_model=OpportunitySchema)
def update_opportunity(
    opportunity_id: str,
    opp_update: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    old_stage = opp.stage

    opp.title = opp_update.title
    opp.agency = opp_update.agency
    opp.account_id = opp_update.account_id
    opp.naics_code = opp_update.naics_code
    opp.set_aside_type = opp_update.set_aside_type
    opp.estimated_value = opp_update.estimated_value
    opp.solicitation_number = opp_update.solicitation_number
    opp.source = opp_update.source
    opp.stage = opp_update.stage
    opp.capture_manager_id = opp_update.capture_manager_id
    opp.expected_release_date = opp_update.expected_release_date
    opp.proposal_due_date = opp_update.proposal_due_date
    opp.award_date_estimate = opp_update.award_date_estimate
    opp.win_probability = opp_update.win_probability
    opp.notes = opp_update.notes

    opp.vehicles = _resolve_vehicles(opp_update.vehicle_ids, db)

    # Auto-create proposal when moving to proposal stage
    if opp_update.stage == "proposal" and old_stage != "proposal" and not opp.proposal:
        proposal = Proposal(
            id=generate_id(),
            opportunity_id=opp.id,
            proposal_manager_id=current_user.id,
            status="not_started",
            submission_deadline=opp_update.proposal_due_date,
        )
        db.add(proposal)

    db.commit()
    db.refresh(opp)
    return opp


@router.patch("/{opportunity_id}", response_model=OpportunitySchema)
def patch_opportunity(
    opportunity_id: str,
    updates: OpportunityPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    old_stage = opp.stage
    update_data = updates.model_dump(exclude_unset=True)

    if "vehicle_ids" in update_data:
        vehicle_ids = update_data.pop("vehicle_ids")
        opp.vehicles = _resolve_vehicles(vehicle_ids, db)

    for field, value in update_data.items():
        setattr(opp, field, value)

    # Auto-create proposal when moving to proposal stage
    new_stage = update_data.get("stage")
    if new_stage == "proposal" and old_stage != "proposal" and not opp.proposal:
        proposal = Proposal(
            id=generate_id(),
            opportunity_id=opp.id,
            proposal_manager_id=current_user.id,
            status="not_started",
            submission_deadline=opp.proposal_due_date,
        )
        db.add(proposal)

    db.commit()
    db.refresh(opp)
    return opp


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    db.delete(opp)
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import batches as Batch, users, RoleEnum
from app.schema.schema import BatchCreate, BatchRead, BatchUpdate
from app.dependencies.role import require_roles

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_batch(data: BatchCreate,db: Session = Depends(get_db),current_user: users = Depends(require_roles(RoleEnum.ADMIN))):
    batch = Batch(
        name=data.name,
        description=data.description,
        coordinator_id=data.coordinator_id,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=data.is_active,
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {
        "message": "Batch created successfully",
        "batch": BatchRead.from_orm(batch),
    }


@router.get("/")
def fetch_batches(db: Session = Depends(get_db),current_user: users = Depends(require_roles(RoleEnum.ADMIN))):
    batches = db.query(Batch).all()
    return {
        "message": "Batches fetched successfully",
        "batches": batches,
    }


@router.get("/{batch_id}")
def fetch_batch_by_id(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "message": "Batch fetched successfully",
        "batch": batch,
    }


@router.put("/{batch_id}")
def update_batch(
    batch_id: int,
    payload: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: users = Depends(require_roles(RoleEnum.ADMIN)),
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if payload.name is not None:
        batch.name = payload.name
    if payload.description is not None:
        batch.description = payload.description
    if payload.coordinator_id is not None:
        batch.coordinator_id = payload.coordinator_id
    if payload.start_date is not None:
        batch.start_date = payload.start_date
    if payload.end_date is not None:
        batch.end_date = payload.end_date
    if payload.is_active is not None:
        batch.is_active = payload.is_active

    db.commit()
    db.refresh(batch)

    return {
        "message": "Batch updated successfully",
        "batch": batch,
    }


@router.delete("/{batch_id}")
def delete_batch(batch_id: int,db: Session = Depends(get_db),current_user: users = Depends(require_roles(RoleEnum.ADMIN))):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    db.delete(batch)
    db.commit()

    return {
        "message": "Batch deleted successfully",
        "batch": batch,
    }

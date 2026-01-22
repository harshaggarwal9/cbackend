from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import batches, teachers, batch_teachers, users, RoleEnum
from app.schema import BatchTeacherCreate, BatchTeacherRead
from app.dependencies.role import require_roles

router = APIRouter(prefix="/allotment", tags=["Allotment"])


@router.post("/", response_model=BatchTeacherRead, status_code=status.HTTP_201_CREATED)
def allot_teacher_to_batch(payload: BatchTeacherCreate,db: Session = Depends(get_db),current_user: users = Depends(require_roles(RoleEnum.ADMIN))):
    batch = db.query(batches).filter(batches.id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    teacher = db.query(teachers).filter(teachers.id == payload.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    existing= db.query(batch_teachers).filter(batch_teachers.batch_id == payload.batch_id,batch_teachers.teacher_id == payload.teacher_id,).first()
    if existing:
        raise HTTPException(status_code=400,detail="Teacher already allotted to this batch",)

    row = batch_teachers(
        batch_id=payload.batch_id,
        teacher_id=payload.teacher_id,
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import (
    contents,
    comments,
    enrollments,
    batches,
    users,
    RoleEnum,
    ContentTypeEnum,
)
from app.schema import ContentRead, CommentCreate, CommentRead
from app.dependencies.role import require_roles
from app.core.authen import get_current_user

router = APIRouter(prefix="/contents", tags=["Contents"])

@router.post("/", response_model=ContentRead, status_code=status.HTTP_201_CREATED)
def upload_content(
    title: str,
    storage_url: str,
    description: str = "",
    content_type: str = "video",
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: users = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.TEACHER)),
):
    if batch_id is not None:
        batch = db.query(batches).filter(batches.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

    content = contents(
        title=title,
        description=description,
        storage_url=storage_url,
        content_type=ContentTypeEnum(content_type),
        uploader_id=current_user.id,
        batch_id=batch_id,
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return content


@router.get("/", response_model=List[ContentRead])
def list_contents(batch_id: Optional[int] = None,only_public: bool = False,db: Session = Depends(get_db)):
    q = db.query(contents)

    if batch_id is not None:
        q = q.filter(contents.batch_id == batch_id)

    if only_public:
        q = q.filter(contents.is_public == True)

    return q.order_by(contents.created_at.desc()).all()


@router.get("/{content_id}", response_model=ContentRead)
def get_content(content_id: int,db: Session = Depends(get_db),current_user: users = Depends(get_current_user),):
    content = db.query(contents).filter(contents.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.batch_id is not None:
        enrolled = db.query(enrollments).filter(enrollments.batch_id == content.batch_id,enrollments.student_id == current_user.id,enrollments.is_active == True,).first()

        if not enrolled and current_user.role != RoleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="Not enrolled in this batch")

    return content


@router.get("/{content_id}/comments", response_model=List[CommentRead])
def list_comments(content_id: int, db: Session = Depends(get_db)):
    content = db.query(contents).filter(contents.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return   db.query(comments).filter(comments.content_id == content_id, comments.is_public == True).order_by(comments.created_at.asc()).all()



@router.post("/{content_id}/comments",response_model=CommentRead,status_code=status.HTTP_201_CREATED)
def create_comment(
    content_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: users = Depends(get_current_user),
):
    content = db.query(contents).filter(contents.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.batch_id is not None:
        enrolled = db.query(enrollments).filter(
            enrollments.batch_id == content.batch_id,
            enrollments.student_id == current_user.id,
            enrollments.is_active == True,
        ).first()

        if not enrolled and current_user.role != RoleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="Not enrolled in this batch")

    comment = comments(
        content_id=content_id,
        author_id=current_user.id,
        text=payload.text,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: users = Depends(get_current_user),
):
    comment = db.query(comments).filter(comments.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.role != RoleEnum.ADMIN and comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

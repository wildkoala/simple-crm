import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models.models import Attachment, Opportunity, User
from app.schemas.schemas import AttachmentSchema
from app.utils import generate_id

router = APIRouter(prefix="/opportunities", tags=["attachments"])

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "uploads",
)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get(
    "/{opportunity_id}/attachments",
    response_model=List[AttachmentSchema],
)
def list_attachments(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opp = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id
    ).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    return (
        db.query(Attachment)
        .filter(Attachment.opportunity_id == opportunity_id)
        .order_by(Attachment.created_at.desc())
        .all()
    )


@router.post(
    "/{opportunity_id}/attachments",
    response_model=AttachmentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    opportunity_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    opp = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id
    ).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    _ensure_upload_dir()

    file_id = generate_id()
    # Preserve extension from original filename
    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[1][:10]
    stored_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    # Read and save file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 50 MB.",
        )

    with open(file_path, "wb") as f:
        f.write(content)

    attachment = Attachment(
        id=file_id,
        opportunity_id=opportunity_id,
        filename=file.filename or "unnamed",
        stored_filename=stored_filename,
        content_type=file.content_type,
        size=len(content),
        uploaded_by_user_id=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{opportunity_id}/attachments/{attachment_id}/download")
def download_attachment(
    opportunity_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    attachment = (
        db.query(Attachment)
        .filter(
            Attachment.id == attachment_id,
            Attachment.opportunity_id == opportunity_id,
        )
        .first()
    )
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    file_path = os.path.join(UPLOAD_DIR, attachment.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.content_type or "application/octet-stream",
    )


@router.delete(
    "/{opportunity_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attachment(
    opportunity_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    attachment = (
        db.query(Attachment)
        .filter(
            Attachment.id == attachment_id,
            Attachment.opportunity_id == opportunity_id,
        )
        .first()
    )
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    # Remove file from disk
    file_path = os.path.join(UPLOAD_DIR, attachment.stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(attachment)
    db.commit()
    return None

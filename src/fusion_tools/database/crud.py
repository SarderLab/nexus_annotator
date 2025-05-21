from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import (
    User, Slide, AnnotationFile, AnnotationData,
    UserAnnotationLabel, UserFileProgress, ActivityStatus
)
import datetime

# --- User CRUD ---
def get_or_create_user(db: Session, id:str, username: str, email: str = None):
    user = db.query(User).filter_by(username=username).first()
    if not user:
        user = User(id= id, username=username, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# --- Slide CRUD ---
def get_slides(db: Session):
    return db.query(Slide).all()

def get_slide_by_internal_id(db: Session, internal_slide_id: int):
    return db.query(Slide).filter(Slide.id == internal_slide_id).first()

def get_slide_by_api_id(db: Session, api_slide_id: str):
    return db.query(Slide).filter(Slide.slide_id == api_slide_id).first()

def get_or_create_slide(db: Session, api_slide_id: str, display_name: str = None):
    slide = get_slide_by_api_id(db, api_slide_id)
    if not slide:
        slide = Slide(slide_id=api_slide_id, display_name=display_name if display_name else api_slide_id)
        db.add(slide)
        db.commit()
        db.refresh(slide)
    return slide

# --- AnnotationFile CRUD ---
def get_annotation_files_for_slide(db: Session, slide_internal_id: int, required_only: bool = False):
    query = db.query(AnnotationFile).filter(AnnotationFile.slide_id == slide_internal_id)
    if required_only:
        query = query.filter(AnnotationFile.is_required_for_completeness == True)
    return query.all()

def get_annotation_file_by_type(db: Session, slide_internal_id: int, file_type: str):
    return db.query(AnnotationFile).filter_by(slide_id=slide_internal_id, file_type=file_type).first()

def get_or_create_annotation_file(db: Session, slide_internal_id: int, file_type: str, file_path: str = None, is_required: bool = False):
    annotation_file = get_annotation_file_by_type(db, slide_internal_id, file_type)
    if not annotation_file:
        annotation_file = AnnotationFile(
            slide_id=slide_internal_id,
            file_type=file_type,
            file_path=file_path,
            is_required_for_completeness=is_required
        )
        db.add(annotation_file)
        db.commit()
        db.refresh(annotation_file)
    elif file_path and annotation_file.file_path != file_path : # Update file_path if changed
        annotation_file.file_path = file_path
        db.commit()
        db.refresh(annotation_file)
    return annotation_file

# --- AnnotationData CRUD ---
def get_annotations_for_file(db: Session, annotation_file_id: int):
    return db.query(AnnotationData).filter_by(annotation_file_id=annotation_file_id).all()

def get_annotation_by_idx(db: Session, annotation_file_id: int, annotation_idx: str):
    return db.query(AnnotationData).filter_by(annotation_file_id=annotation_file_id, annotation_idx=annotation_idx).first()


# --- UserAnnotationLabel CRUD ---
def get_user_labels_for_file(db: Session, user_id: int, annotation_file_id: int):
    return (
        db.query(UserAnnotationLabel)
        .join(AnnotationData, UserAnnotationLabel.annotation_id == AnnotationData.id)
        .filter(
            UserAnnotationLabel.user_id == user_id,
            AnnotationData.annotation_file_id == annotation_file_id
        )
        .all()
    )

def create_or_update_user_label(db: Session, user_id: int, annotation_id: int, label: str):
    entry = (
        db.query(UserAnnotationLabel)
        .filter_by(user_id=user_id, annotation_id=annotation_id)
        .first()
    )
    now = datetime.datetime.utcnow()
    if entry:
        entry.label = label
        entry.updated_at = now
    else:
        entry = UserAnnotationLabel(
            user_id=user_id, annotation_id=annotation_id, label=label, created_at=now, updated_at=now
        )
        db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_user_label(db: Session, user_id: int, annotation_id: int):
    return (
        db.query(UserAnnotationLabel)
        .filter_by(user_id=user_id, annotation_id=annotation_id)
        .first()
    )

# --- Progress tracking ---
def get_or_create_file_progress(db: Session, user_id: int, annotation_file_id: int):
    entry = (
        db.query(UserFileProgress)
        .filter_by(user_id=user_id, annotation_file_id=annotation_file_id)
        .first()
    )
    if not entry:
        entry = UserFileProgress(
            user_id=user_id, annotation_file_id=annotation_file_id,
            status=ActivityStatus.PENDING, percent_complete=0,
            last_updated=datetime.datetime.utcnow()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
    return entry

def update_file_progress(db: Session, user_id: int, annotation_file_id: int):
    # Calculate percent completion and update status
    total = db.query(AnnotationData).filter_by(annotation_file_id=annotation_file_id).count()
    labeled = (
        db.query(UserAnnotationLabel)
        .join(AnnotationData, UserAnnotationLabel.annotation_id == AnnotationData.id)
        .filter(
            UserAnnotationLabel.user_id == user_id,
            AnnotationData.annotation_file_id == annotation_file_id
        )
        .count()
    )
    percent_complete = int(100 * labeled / total) if total else 0
    if percent_complete == 0:
        status = ActivityStatus.PENDING
    elif percent_complete == 100:
        status = ActivityStatus.COMPLETED
    else:
        status = ActivityStatus.IN_PROGRESS

    entry = get_or_create_file_progress(db, user_id, annotation_file_id)
    entry.percent_complete = percent_complete
    entry.status = status
    entry.last_updated = datetime.datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return entry

# --- Helper: Get next unlabeled annotation for user ---
def get_next_unlabeled_annotation(db: Session, user_id: int, annotation_file_id: int):
    # Returns the next AnnotationData in this file the user hasn't labeled yet
    subq = (
        db.query(UserAnnotationLabel.annotation_id)
        .filter(UserAnnotationLabel.user_id == user_id)
        .subquery()
    )
    return (
        db.query(AnnotationData)
        .filter(
            AnnotationData.annotation_file_id == annotation_file_id,
            ~AnnotationData.id.in_(subq)
        )
        .order_by(AnnotationData.id)
        .first()
    )

# --- High-level: Mark label and update progress ---
def label_annotation_and_update_progress(db: Session, user_id: int, annotation_id: int, label: str):
    label_entry = create_or_update_user_label(db, user_id, annotation_id, label)
    annotation = db.query(AnnotationData).filter_by(id=annotation_id).first()
    update_file_progress(db, user_id, annotation.annotation_file_id)
    return label_entry

# --- Progress summary for a slide (aggregates files) ---
def get_slide_progress_summary(db: Session, user_id: int, slide_id: int):
    files = get_annotation_files_for_slide(db, slide_id)
    summary = []
    for f in files:
        prog = (
            db.query(UserFileProgress)
            .filter_by(user_id=user_id, annotation_file_id=f.id)
            .first()
        )
        summary.append({
            "file_type": f.file_type,
            "percent_complete": prog.percent_complete if prog else 0,
            "status": prog.status.value if prog else "pending",
        })
    return summary


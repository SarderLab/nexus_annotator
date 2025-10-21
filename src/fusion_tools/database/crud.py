from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import (
    User, Slide, AnnotationFile, AnnotationData,
    UserAnnotationLabel, UserFileProgress, ActivityStatus
)
import datetime
from typing import Optional

# --- User CRUD ---
def get_or_create_user(db: Session, id:str, username: str, email: str = None):
    user = db.query(User).filter_by(id=id).first()
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

def populate_annotations_from_file(db: Session, annotation_file_id: int, annotation_definitions: list[dict]):
    """
    Populates AnnotationData from a list of definitions. Each definition is a dict
    expected to have 'annotation_idx' and 'bbox' (as a string).
    Avoids creating duplicates based on annotation_idx for the given annotation_file_id.
    Returns a list of created or existing AnnotationData objects.
    """
    existing_idxs = {
        ad.annotation_idx for ad in 
        db.query(AnnotationData.annotation_idx).filter_by(annotation_file_id=annotation_file_id).all()
    }
    
    new_annotations = []
    created_count = 0
    for entry in annotation_definitions:
        idx = entry.get("annotation_idx")
        bbox_str = entry.get("bbox")
        if not idx:
            print(f"Skipping annotation entry due to missing 'annotation_idx' for file_id {annotation_file_id}")
            continue
            
        if idx not in existing_idxs:
            annotation = AnnotationData(
                annotation_file_id=annotation_file_id,
                annotation_idx=idx,
                bbox=bbox_str
            )
            new_annotations.append(annotation)
            existing_idxs.add(idx) # Add to set to prevent duplicates from same input list
            created_count +=1

    if new_annotations:
        db.add_all(new_annotations)
        db.commit()
        print(f"Added {created_count} new annotations for file_id {annotation_file_id}.")
    
    # Return all annotations for the file, including newly created and pre-existing ones
    return db.query(AnnotationData).filter_by(annotation_file_id=annotation_file_id).all()

# --- UserAnnotationLabel CRUD ---
def get_user_labels_for_file(db: Session, user_id: str, annotation_file_id: int):
    return (
        db.query(UserAnnotationLabel)
        .join(AnnotationData, UserAnnotationLabel.annotation_id == AnnotationData.id)
        .filter(
            UserAnnotationLabel.user_id == user_id,
            AnnotationData.annotation_file_id == annotation_file_id
        )
        .all()
    )

def create_or_update_user_label(db: Session, user_id: str, annotation_id: int, label_name: str, label_value: str, label_comment: Optional[str] = None): # user_id to str
    entry = (
        db.query(UserAnnotationLabel)
        .filter_by(user_id=user_id, annotation_id=annotation_id, label_name=label_name) # Query by label_name
        .first()
    )
    now = datetime.datetime.utcnow()
    if entry:
        if entry.label_value != label_value or entry.label_comment != label_comment:
            entry.label_value = label_value
            entry.label_comment = label_comment
            entry.updated_at = now
            db.commit()
            db.refresh(entry)
    else:
        entry = UserAnnotationLabel(
            user_id=user_id, 
            annotation_id=annotation_id, 
            label_name=label_name,
            label_value=label_value, 
            label_comment=label_comment,
            created_at=now, 
            updated_at=now
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
    return entry


def get_user_label_by_name(db: Session, user_id: str, annotation_id: int, label_name: str): # user_id to str
    return (
        db.query(UserAnnotationLabel)
        .filter_by(user_id=user_id, annotation_id=annotation_id, label_name=label_name)
        .first()
    )

def delete_user_label_by_name(db: Session, user_id: str, annotation_id: int, label_name: str):
    """
    Deletes a UserAnnotationLabel entry based on user_id, annotation_id, and label_name.
    """
    entry = (
        db.query(UserAnnotationLabel)
        .filter_by(user_id=user_id, annotation_id=annotation_id, label_name=label_name)
        .first()
    )
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False

# --- Progress tracking ---
def get_or_create_file_progress(db: Session, user_id: int, annotation_file_id: int):
    entry = (
        db.query(UserFileProgress)
        .filter_by(user_id=user_id, annotation_file_id=annotation_file_id)
        .first()
    )
    if entry:
        return entry
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
    total_annotations = db.query(func.count(AnnotationData.id)).filter_by(annotation_file_id=annotation_file_id).scalar()
    
    labeled_annotations = (
        db.query(func.count(UserAnnotationLabel.annotation_id.distinct()))
        .join(AnnotationData, UserAnnotationLabel.annotation_id == AnnotationData.id)
        .filter(
            UserAnnotationLabel.user_id == user_id,
            AnnotationData.annotation_file_id == annotation_file_id
        )
        .scalar()
    )
    
    percent_complete = int(100 * labeled_annotations / total_annotations) if total_annotations and total_annotations > 0 else 0
    
    if percent_complete == 0:
        status = ActivityStatus.PENDING
    elif percent_complete == 100:
        status = ActivityStatus.COMPLETED
    else:
        status = ActivityStatus.IN_PROGRESS

    entry = get_or_create_file_progress(db, user_id, annotation_file_id) # Ensures entry exists
    
    # Check if update is necessary
    if entry.percent_complete != percent_complete or entry.status != status:
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
def label_annotation_and_update_progress(db: Session, user_id: str, annotation_id: int, label_name: str, label_value: str, label_comment: Optional[str] = None): # user_id to str, added label_name, value, comment
    label_entry = create_or_update_user_label(db, user_id, annotation_id, label_name, label_value, label_comment)
    
    annotation = db.query(AnnotationData.annotation_file_id).filter_by(id=annotation_id).scalar()
    if annotation_file_id := annotation:
        update_file_progress(db, user_id, annotation_file_id)
    else:
        print(f"Could not find annotation_file_id for annotation_id {annotation_id} to update progress.")
    return label_entry

# --- Progress summary for a slide (aggregates files) ---
def get_slide_progress_summary_for_user(db: Session, user_id: str, slide_internal_id: int = None, slide_id: int = None, required_only: bool = False, task_identifier: str = None): 
    if slide_internal_id is None and slide_id is not None:
        slide = db.query(Slide).filter(Slide.slide_id == slide_id).first()
        if not slide:
            return 0.0, False, []
        slide_internal_id = slide.id
    
    if slide_internal_id is None:
        return 0.0, False, []
    file_query = db.query(AnnotationFile).filter(AnnotationFile.slide_id == slide_internal_id)
    #THIS CHECK NEEDS TO BE DONE - DUE TO PROD DATABSE HAVING INCONSISTENT ENTIRES AND AS FILTERING IS DONE IN SEGMENTATION.PY, WE CAN SKIP THIS.
    if required_only:
        file_query = file_query.filter(AnnotationFile.is_required_for_completeness == True)
    if task_identifier is not None:
        file_query = file_query.filter(AnnotationFile.file_type.like(f"{task_identifier}_%"))
    
    files_to_check = file_query.all()
    if not files_to_check: # Still no files after attempting to get all
        return 0.0, False, []

    
    total_annotations_for_slide = 0
    total_labeled_annotations_for_slide = 0
    all_completed_flag = True
    progress_details = []

    for f in files_to_check:

        prog_entry = get_or_create_file_progress(db, user_id, f.id)
        
        file_total_annotations = db.query(func.count(AnnotationData.id)).filter_by(annotation_file_id=f.id).scalar()
        file_labeled_annotations = (
            db.query(func.count(UserAnnotationLabel.annotation_id.distinct()))
            .join(AnnotationData, UserAnnotationLabel.annotation_id == AnnotationData.id)
            .filter(
                UserAnnotationLabel.user_id == user_id,
                AnnotationData.annotation_file_id == f.id
            )
            .scalar()
        )
        
        total_annotations_for_slide += file_total_annotations
        total_labeled_annotations_for_slide += file_labeled_annotations
        
        if prog_entry.status != ActivityStatus.COMPLETED:
            all_completed_flag = False
        
        progress_details.append({
            "file_type": f.file_type,
            "annotation_file_id": f.id,
            "percent_complete": prog_entry.percent_complete,
            "status": prog_entry.status.value, # prog_entry is guaranteed by get_or_create
            "is_required": f.is_required_for_completeness
        })

    if total_annotations_for_slide == 0: 
        return 0.0, True if not files_to_check else False, [] # If no files were processed (e.g. all filtered out, or no progress entries made)

    average_completeness = (total_labeled_annotations_for_slide / total_annotations_for_slide) * 100 if total_annotations_for_slide > 0 else 0
    return average_completeness, all_completed_flag, progress_details
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
        if entry.label != label:
            entry.label = label
            entry.updated_at = now
            db.commit()
            db.refresh(entry)
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
    total_annotations = db.query(func.count(AnnotationData.id)).filter_by(annotation_file_id=annotation_file_id).scalar()
    
    labeled_annotations = (
        db.query(func.count(UserAnnotationLabel.id))
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
def label_annotation_and_update_progress(db: Session, user_id: int, annotation_id: int, label: str):
    # annotation_id is AnnotationData.id
    label_entry = create_or_update_user_label(db, user_id, annotation_id, label)
    
    # Get annotation_file_id from the annotation_id
    annotation = db.query(AnnotationData.annotation_file_id).filter_by(id=annotation_id).scalar_one_or_none()
    if annotation_file_id := annotation: # Check if not None
        update_file_progress(db, user_id, annotation_file_id) # Mypy might complain if annotation_file_id could be None
    else:
        print(f"Could not find annotation_file_id for annotation_id {annotation_id} to update progress.")

    return label_entry

# --- Progress summary for a slide (aggregates files) ---
def get_slide_progress_summary_for_user(db: Session, user_id: int, slide_internal_id: int, required_only: bool = False):
    """
    Calculates overall slide progress for a user based on 'required' AnnotationFiles.
    Returns:
        - average_completeness (float): Average percentage across required files.
        - all_required_completed (bool): True if all required files are 100% complete.
        - details (list): List of dicts with progress for each required file.
    """
    required_files = get_annotation_files_for_slide(db, slide_internal_id, required_only=True)
    
    if not required_files and required_only: # If we only care about required files and there are none defined as such
        return 0.0, True, [] # No required work, so it's "complete" in a vacuum, or 0% if you prefer. Let's say 0% and not all_complete.
                                   # This depends on desired behavior if no structures are marked as required.
                                   # Assuming if required_only=True and no files are required, slide is not considered complete by default.
                                   # If required_only=False, it calculates for all files.

    if not required_files: # No annotation files at all for this slide (required or not)
        return 0.0, True, [] # Or False if empty means not complete

    total_percent_sum = 0
    num_required_files_processed = 0
    all_completed_flag = True
    progress_details = []

    files_to_check = required_files if required_only and required_files else get_annotation_files_for_slide(db, slide_internal_id, required_only=False)
    if not files_to_check: # No files to check implies 0% completion
        return 0.0, False, []


    for f in files_to_check:
        if required_only and not f.is_required_for_completeness: # Should not happen if required_files query is correct
            continue

        prog_entry = get_or_create_file_progress(db, user_id, f.id)
        
        total_percent_sum += prog_entry.percent_complete
        num_required_files_processed += 1
        if prog_entry.status != ActivityStatus.COMPLETED:
            all_completed_flag = False
        
        progress_details.append({
            "file_type": f.file_type,
            "annotation_file_id": f.id,
            "percent_complete": prog_entry.percent_complete,
            "status": prog_entry.status.value if prog_entry else ActivityStatus.PENDING.value, # Ensure prog_entry exists
            "is_required": f.is_required_for_completeness
        })

    if num_required_files_processed == 0: # No required files had progress entries or no required files exist
        # This case depends on interpretation: if no required work, is it 100% complete or 0%?
        # Let's assume if no required files are defined and we ask for required_only, it means nothing to do, so 0% to show up.
        return 0.0, False, [] 

    average_completeness = total_percent_sum / num_required_files_processed
    return average_completeness, all_completed_flag, progress_details
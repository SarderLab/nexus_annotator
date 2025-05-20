import datetime
import enum
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column

Base = declarative_base()

class ActivityStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(String, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    annotation_labels = relationship("UserAnnotationLabel", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserFileProgress", back_populates="user", cascade="all, delete-orphan")

class Slide(Base):
    __tablename__ = "slides"
    id: Mapped[int] = mapped_column(String, primary_key=True, autoincrement=False)
    slide_id: Mapped[str] = mapped_column(String, unique=True, index=True)   # e.g., filename or UUID
    display_name: Mapped[Optional[str]] = mapped_column(String)

    annotation_files = relationship("AnnotationFile", back_populates="slide", cascade="all, delete-orphan")

class AnnotationFile(Base):
    __tablename__ = "annotation_files"
    id: Mapped[int] = mapped_column(String, primary_key=True, autoincrement=False)
    slide_id: Mapped[int] = mapped_column(ForeignKey("slides.id"), nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)           # e.g., 'glomerulus', 'tubule'
    file_path: Mapped[str] = mapped_column(String, nullable=True)            # optional, where the file is on disk/api

    slide = relationship("Slide", back_populates="annotation_files")
    annotations = relationship("AnnotationData", back_populates="annotation_file", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("slide_id", "file_type", name="_slide_file_uc"),)

class AnnotationData(Base):
    __tablename__ = "annotation_data"
    id: Mapped[int] = mapped_column(String, primary_key=True, autoincrement=False)
    annotation_file_id: Mapped[int] = mapped_column(ForeignKey("annotation_files.id"), nullable=False)
    annotation_idx: Mapped[str] = mapped_column(String, nullable=False)      # unique id in file (e.g., index, or object id)
    bbox: Mapped[Optional[str]] = mapped_column(String)                      # store bbox as stringified JSON or separate columns

    annotation_file = relationship("AnnotationFile", back_populates="annotations")
    user_labels = relationship("UserAnnotationLabel", back_populates="annotation", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("annotation_file_id", "annotation_idx", name="_file_annotation_uc"),)

class UserAnnotationLabel(Base):
    __tablename__ = "user_annotation_labels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotation_data.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="annotation_labels")
    annotation = relationship("AnnotationData", back_populates="user_labels")

    __table_args__ = (UniqueConstraint("user_id", "annotation_id", name="_user_annotation_uc"),)

class UserFileProgress(Base):
    __tablename__ = "user_file_progress"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    annotation_file_id: Mapped[int] = mapped_column(ForeignKey("annotation_files.id"), nullable=False)
    status: Mapped[ActivityStatus] = mapped_column(SQLEnum(ActivityStatus), nullable=False, default=ActivityStatus.PENDING)
    percent_complete: Mapped[float] = mapped_column(Integer, default=0)  # store as int or float (0-100)
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="progress")
    # Optionally, annotation_file = relationship("AnnotationFile")

    __table_args__ = (UniqueConstraint("user_id", "annotation_file_id", name="_user_file_progress_uc"),)

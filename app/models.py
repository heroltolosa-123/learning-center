import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, UniqueConstraint
)
from sqlalchemy.orm import relationship
from .database import Base


def now():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=now)

    enrollments = relationship("Enrollment", back_populates="user")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    thumbnail_url = Column(String(500), default="")
    price_php = Column(Numeric(10, 2), nullable=False, default=0)
    is_published = Column(Boolean, default=False, nullable=False)
    instructor_name = Column(String(255), default="")
    category = Column(String(100), default="")
    level = Column(String(20), default="")  # Beginner | Intermediate | Advanced | ""
    created_at = Column(DateTime, default=now)

    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.order", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")

    @property
    def is_free(self):
        return self.price_php is None or float(self.price_php) <= 0


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, default="")  # markdown/plain text body
    video_url = Column(String(500), default="")  # embeddable video URL (YouTube/Vimeo/etc)
    order = Column(Integer, default=0, nullable=False)
    is_preview = Column(Boolean, default=False, nullable=False)  # viewable without purchase

    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending | paid | failed
    created_at = Column(DateTime, default=now)
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    payments = relationship("Payment", back_populates="enrollment")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    paymongo_checkout_session_id = Column(String(255), index=True, nullable=True)
    paymongo_payment_intent_id = Column(String(255), index=True, nullable=True)
    amount_php = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending | paid | failed | expired
    raw_event = Column(Text, default="")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    enrollment = relationship("Enrollment", back_populates="payments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed_at = Column(DateTime, default=now)

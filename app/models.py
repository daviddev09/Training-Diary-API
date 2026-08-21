from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import Difficulty, UserRole
from app.core.security import create_uuid7


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=create_uuid7
    )
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    username: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    password: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int]
    current_weight: Mapped[float | None] = mapped_column(default=None)

    diaries: Mapped[list["Diary"]] = relationship(
        back_populates="user",
        order_by="Diary.id",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_weights: Mapped[list["Weight"]] = relationship(
        back_populates="user",
        order_by="Weight.id",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    token: Mapped["RefreshSession"] = relationship(
        back_populates="user",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Diary(Base):
    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE")
    )
    diary_name: Mapped[str] = mapped_column(String(30), default="Training diary")

    user: Mapped["User"] = relationship(back_populates="diaries")
    training_days: Mapped[list["TrainingDay"]] = relationship(
        back_populates="diary",
        order_by="TrainingDay.id",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TrainingDay(Base):
    __tablename__ = "training_days"

    id: Mapped[int] = mapped_column(primary_key=True)
    diary_id: Mapped[int] = mapped_column(ForeignKey("diaries.id", ondelete="CASCADE"))
    date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    difficulty: Mapped[Difficulty | None]
    total_time_seconds: Mapped[int | None]

    diary: Mapped["Diary"] = relationship(back_populates="training_days")
    circuits: Mapped[list["Circuit"]] = relationship(
        back_populates="training_day",
        order_by="Circuit.numberation",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Circuit(Base):
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    training_day_id: Mapped[int] = mapped_column(
        ForeignKey("training_days.id", ondelete="CASCADE")
    )
    numberation: Mapped[int]

    training_day: Mapped["TrainingDay"] = relationship(back_populates="circuits")
    exercises: Mapped[list["CompletedExercise"]] = relationship(
        back_populates="circuit",
        order_by="CompletedExercise.id",
        lazy="raise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CompletedExercise(Base):
    __tablename__ = "completed_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(
        ForeignKey("circuits.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    duration_seconds: Mapped[int | None] = mapped_column(default=None)
    reps: Mapped[int | None]
    rest_seconds: Mapped[int | None]

    circuit: Mapped["Circuit"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(
        back_populates="added_exercises", lazy="raise"
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    added_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.uuid", ondelete="SET NULL")
    )
    is_system: Mapped[bool] = mapped_column(default=False)

    added_exercises: Mapped[list["CompletedExercise"]] = relationship(
        back_populates="exercise"
    )


class Weight(Base):
    __tablename__ = "weights"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE")
    )
    weight: Mapped[float]
    added_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="user_weights")


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE")
    )

    token: Mapped[str] = mapped_column(nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="token")

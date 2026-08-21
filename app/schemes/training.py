from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import Difficulty


class DiaryCreate(BaseModel):
    diary_name: str = Field(max_length=30, min_length=1)


class TrainingDayCreate(BaseModel):
    date: datetime | None = Field(default=None)
    difficulty: Difficulty | None = Field(default=None)
    total_time_seconds: int | None = Field(default=None, lt=86400)


class ComplExerciseCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    duration_seconds: int | None = Field(ge=0, lt=86400, default=None)
    reps: int | None = Field(ge=0, lt=86400, default=None)
    rest_seconds: int | None = Field(ge=0, lt=86400, default=None)


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=30)
    description: str | None = Field(default=None, max_length=500)


class DiaryUpdate(BaseModel):
    diary_name: str = Field(max_length=30, min_length=1)


class TrainingDayUpdate(BaseModel):
    date: datetime | None = Field(default=None)
    difficulty: Difficulty | None = Field(default=None)
    total_time_seconds: int | None = Field(default=None, lt=86400)


class ComplExerciseUpdate(BaseModel):
    duration_seconds: int | None = Field(ge=0, lt=86400, default=None)
    reps: int | None = Field(ge=0, lt=86400, default=None)
    rest_seconds: int | None = Field(ge=0, lt=86400, default=None)


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=30)
    description: str | None = Field(default=None, max_length=500)


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    is_system: bool
    description: str | None = Field(default=None)


class ComplExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="Postgres PK")
    exercise_id: int
    duration_seconds: int | None = Field(default=None)
    reps: int | None = Field(default=None)
    rest_seconds: int | None = Field(default=None)


class CircuitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numberation: int

    exercises: list[ComplExerciseRead] = Field(default_factory=list)


class TrainingDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    diary_id: int | None = Field(default=None, description="Postgres FK")
    date: datetime | None = Field(default=None)
    difficulty: Difficulty | None = Field(default=None)
    total_time_seconds: int | None = Field(default=None)

    circuits: list[CircuitRead] = Field(default_factory=list)


class DiaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="Postgres PK")
    diary_name: str
    training_days: list[TrainingDayRead] = Field(default_factory=list)


class OnlyDiaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    diary_name: str


class OnlyTrainingDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    diary_id: int
    date: datetime
    difficulty: Difficulty | None = Field(default=None)
    total_time_seconds: int | None = Field(default=None)


class OnlyCircuitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    training_day_id: int
    numberation: int

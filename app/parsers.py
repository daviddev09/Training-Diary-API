from typing import Any


def guest_diary_parser(data: dict[str, Any]) -> dict[str, Any]:
    from app.models import Circuit, CompletedExercise, Diary, TrainingDay
    from app.schemes.training import DiaryRead

    training_days = None
    diary_dto = DiaryRead.model_validate(data)

    diary_model = Diary(diary_name=diary_dto.diary_name)

    if diary_dto.training_days:
        training_days = diary_dto.training_days.copy()

    if training_days:
        for training_day in training_days:
            tr_day_model = TrainingDay(
                date=training_day.date,
                difficulty=training_day.difficulty,
                total_time_seconds=training_day.total_time_seconds,
            )

            circuits = None
            if training_day.circuits:
                circuits = training_day.circuits.copy()

            if circuits:
                for circuit in circuits:
                    circuit_model = Circuit(numberation=circuit.numberation)

                    exercises = None
                    if circuit.exercises:
                        exercises = circuit.exercises.copy()

                    if exercises:
                        for ex in exercises:
                            exercise_model = CompletedExercise(
                                exercise_id=ex.exercise_id,
                                duration_seconds=ex.duration_seconds,
                                reps=ex.reps,
                                rest_seconds=ex.rest_seconds,
                            )
                            circuit_model.exercises.append(exercise_model)

                    tr_day_model.circuits.append(circuit_model)
            diary_model.training_days.append(tr_day_model)
    return {
        "diary_name": diary_model.diary_name,
        "training_days": diary_model.training_days,
    }

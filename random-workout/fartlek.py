import random

from .utils import mmss_to_seconds, pace_to_ms, seconds_to_mmss
from .workout import Workout, WorkoutStep, Target


def fartlek(target_time):
    target_seconds = mmss_to_seconds(target_time)

    if target_seconds >= 40 * 60:
        # runs longer than 40 minutes == 10 minutes warmup/cooldown
        warmup = 10*60
        cooldown = warmup
    elif target_seconds >= 25 * 60:
        # runs longer than 25 minutes == 8 minutes warmup + 4 minutes cooldown
        warmup = 8*60
        cooldown = 4*60
    else:
        # all other runs get a default 5 minutes warmup and 3 minutes cooldown
        warmup = 5*60
        cooldown = 2*60

    workout = [warmup, cooldown]

    while sum(workout) < target_seconds:
        # add an interval-recovery rep
        interval = 15 * random.randint(2, 8)
        recovery = interval + 15 * random.randint(2, 4)

        workout.insert(-1, interval)
        workout.insert(-1, recovery)

    if sum(workout) > target_seconds:
        # remove the last interval and increase by the time left
        workout.pop(-2) + workout.pop(-2)
        remaining = target_seconds - sum(workout)
        i = random.randint(1, len(workout) - 1)
        workout[i] += remaining

    return workout


def create_fartlek_workout(duration, target_pace, name=None):
    workout_steps = fartlek(duration)
    target_min = round(pace_to_ms(target_pace), 1)
    target_max = round(pace_to_ms(target_pace) * 0.85, 1)

    if not name:
        name = f"Running workout ({duration})"
        workout = Workout('running', name)
        workout.add_step(
            WorkoutStep(
                1, "warmup", end_condition="time", end_condition_value=seconds_to_mmss(workout_steps.pop(0))
            )
        )

        for i, step in enumerate(workout_steps[:-1]):
            step_type = "interval" if i % 2 == 0 else "recovery"
            target = (
                Target("pace.zone", target_min, target_max)
                if step_type == 'interval'
                else Target()
            )
            workout.add_step(WorkoutStep(i+2, step_type, end_condition='time', end_condition_value=seconds_to_mmss(step), target=target))

        workout.add_step(WorkoutStep(len(workout.workout_steps)+1, "cooldown", end_condition='time', end_condition_value=seconds_to_mmss(workout_steps[-1])))

        return workout

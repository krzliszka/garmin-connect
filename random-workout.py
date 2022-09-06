#! /usr/bin/env python
import json
import sys

from random-workout.garmin import  GarminClient
from random-workout.fartlek import create_fartlek_workout

def parse_args(args):
    result = {
        
    }

def get_or_throw(d, key, error):
    try:
        return d[key]
    except:
        raise Exception(error)

if __name__ == "__main__":
    args = parse_args(sys.argv)

    duration = get_or_throw(args, "--duration", "The --duration value is required (format: MM:SS")
    target_pace = get_or_throw(args, "--target-pace", "The --target-pace value is required (format: MM:SS - mins/km")

    if not "--dry-run" in args:
        username = get_or_throw(args, "--username", "The Garmin Connect --username value is required")
        password = get_or_throw(args, "--password", "The Garmin Connect --password value is required")

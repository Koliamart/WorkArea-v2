from enum import Enum


class TaskStatus(str, Enum):
    new = 'new'
    in_progress = 'in_progress'
    done = 'done'


class TaskPriority(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

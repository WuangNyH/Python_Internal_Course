from enum import StrEnum


class Permissions(StrEnum):
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ASSIGN_ROLE = "user:assign_role"

    STUDENT_READ = "student:read"
    STUDENT_WRITE = "student:write"
    STUDENT_DELETE = "student:delete"

    TASK_READ = "task:read"
    TASK_WRITE = "task:write"
    TASK_DELETE = "task:delete"
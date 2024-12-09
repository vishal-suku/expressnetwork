ORGANIZATION_ADMIN: str = "admin"
ORGANIZATION_MANAGER: str = "manager"
ORGANIZATION_SCHEDULER: str = "scheduler"
ORGANIZATION_USER: str = "user"

CHANGE_PASSWORD_BROWSER_URL: str = "change-password"
ALLOWED_RANDOM_CHARS: str = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


class UserActivity:
    LOGIN = "User Login"
    LOGOUT = "User Logout"
    PASSWORD_CHANGED = "Password Changed"


TRY_ERROR_MESSAGE = "Sorry, but it seems you've exceeded the maximum number of login attempts with incorrect credentials. For security reasons, we've temporarily locked your account."
MAXIMUM_TRY_COUNT = 3
MAXIMUM_TRY_STATUS = 211

USER_SESSION_REPORT_MAILS = {"Develop": ["vishalu1438@gmail.com"],
                             "Staging": ["vishalu1438@gmail.com"],
                             "Production":["vishalu1438@gmail.com"]}
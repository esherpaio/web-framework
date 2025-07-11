from web.database.model import UserRole, UserRoleId, UserRoleLevel

user_role_seeds = [
    UserRole(id=UserRoleId.GUEST, name="Guest", level=UserRoleLevel.GUEST),
    UserRole(id=UserRoleId.USER, name="User", level=UserRoleLevel.USER),
    UserRole(id=UserRoleId.EXTERNAL, name="External", level=UserRoleLevel.EXTERNAL),
    UserRole(id=UserRoleId.ADMIN, name="Admin", level=UserRoleLevel.ADMIN),
    UserRole(id=UserRoleId.SUPER, name="Super", level=UserRoleLevel.SUPER),
]

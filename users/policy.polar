# Roles
user_role(user, "admin") if
    user.is_admin;

user_role(user, "user") if
    not user.is_admin;

# Permissions
allow(user, "manage_roles", _) if
    user_role(user, "admin");

allow(user, "view_profile", resource) if
    user_role(user, "user") and
    user.id = resource.id;

allow(user, "delete_user", resource) if
    user_role(user, "user") and
    user.id = resource.id;

allow(user, "update_profile", resource) if
    user_role(user, "user") and
    user.id = resource.id;

allow(user, "view_all_users", _) if
    user_role(user, "admin");

allow(user, "create_user", _user) if
    user_role(user, "admin");
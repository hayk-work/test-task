# Roles
user_role(user, "admin") if
    user.is_admin;

user_role(user, "user") if
    not user.is_admin;

# Permissions
allow(_user, "upload", _Document);

allow(user, "query", resource) if
    resource.uploaded_by.id = user.id;

allow(user, "query", _resource) if
    user.is_admin = true;

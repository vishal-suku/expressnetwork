from users import functions, configurations, models
from generics import exceptions

def create_hub(name, email, phone, location, role, request_user):
    """
    Creates a hub with given details
    """
    password_str, password_hash = functions.get_hashed_password(allowed_chars=configurations.ALLOWED_RANDOM_CHARS)
    hub = models.Organization.objects.filter(email=email).first()
    if hub:
        if hub.is_active:
            raise exceptions.ExistsError(detail="User already exists.")
    user = models.User.objects.filter(username=request_user).first()
    if user:
        models.Organization.objects.create(name = name, is_active = True, email = email, phone=phone, location = location, password = password_hash, created_by=user, updated_by=user).save()
        models.Profile.objects.create(user=user, phone=phone, is_active=True, created_by=user, updated_by=user).save()
    return True


def create_enterprise_user(first_name: str, last_name: str, email: str, phone:int, role: str , request_user) -> bool:
    """
    Creates a user with given details
    """

    password_str, password_hash = functions.get_hashed_password(allowed_chars=configurations.ALLOWED_RANDOM_CHARS)
    
    user = models.User.objects.filter(username=email).first()
    if user:
        if user.is_active:
            raise exceptions.ExistsError(detail="User already exists.")
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.last_login = None
            user.is_active = True
            user.password = make_password(password_str)
            profile = get_profile_by_user(user=user)
            profile.phone = phone
            profile.is_active = True
            profile.created_by = request_user
            profile.updated_by = request_user
            user.save()
            profile.save
    else:
        ce = functions.create_enterprise_user(first_name, last_name, email, phone, password_hash, role , request_user)
        if not ce:
            return False

    email_args = {
        'full_name' : f"{first_name} {last_name}".strip(),
        'email'     : email,
        'password'  : password_str,
        'origin'    : settings.SITE_ORIGIN,
    }
    # Send Email as non blocking thread. Reduces request waiting time.
    t = threading.Thread(target=functions.EmailService(email_args, [email, ]).send_welcome_email)
    t.start()
    return True

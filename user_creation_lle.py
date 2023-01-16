from django.contrib.auth.models import User, Group
from django.db import IntegrityError, transaction

from lms.models import UserPasswordHistory, UserRole, StoreRep, Store, Retailer


def create_store_rep_user(username, password, email, store_id, telesales=False):
    with transaction.atomic():
        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
        user.save()
        UserPasswordHistory.add_user_password_history(user.password, user)
        profile = user.get_profile()
        profile.role = UserRole.objects.get(name=UserRole.ROLE_RETAILER_REP)
        profile.save()

        # Group
        if telesales:
            user.groups.add(Group.objects.get(name="TELESALES_AGENT"))
            user.save()

        # StoreRep
        store_rep = StoreRep.objects.create(user=user, store=Store.objects.get(id=store_id))
        user.storerep_set.add(store_rep)
        user.save()


def create_retailer_admin_user(username, password, email, retailer_id):
    with transaction.atomic():
        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
        user.save()
        UserPasswordHistory.add_user_password_history(user.password, user)
        try:
            profile = user.get_profile()
        except:
            profile = user.userprofile
        profile.role = UserRole.objects.get(name=UserRole.ROLE_RETAILER_ADMIN)
        profile.save()

        retailer = Retailer.objects.filter(id=retailer_id).first()
        if retailer:
            retailer.user.add(user)
            retailer.save()


def create_admin_user(username, password, email, force_update=True):
    user = None
    try:

        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
        user.save()
    except IntegrityError as e:
        if not force_update:
            raise Exception(e)

        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.save()

        try:
            profile = user.get_profile()
        except:
            profile = user.userprofile

        profile.email_lower = email
        profile.save()

    UserPasswordHistory.add_user_password_history(user.password, user)
    try:
        profile = user.get_profile()
    except:
        profile = user.userprofile
    profile.role = UserRole.objects.get(name=UserRole.ROLE_ZBY_ADMIN)
    profile.save()
    try:
        user.groups = User.objects.get(username="nadim.cognical").groups.all()
    except:
        user.groups.set(User.objects.get(username="nadim.cognical").groups.all())
    user.is_staff = True
    user.is_superuser = True
    user.save()


# create_retailer_admin_user("NewRetailerAdmin", "@Ka2423413579#", "jesse.zahrt@katapult.com", 10)

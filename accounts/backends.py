from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL
    using email insted of username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel._default_manager.get(email=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            # NOTE: If used alongside built-in backend, this backend should be
            # used first and following line should be commented,
            # since Django's backend already takes care of time difference.
            # UserModel().set_password(password)
            pass
        else:
            if (user.check_password(password)
                    and self.user_can_authenticate(user)):
                return user

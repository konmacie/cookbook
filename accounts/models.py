from django.db import models
from django.contrib.auth.models import User

# Make 'email' field of user model unique and required
User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False

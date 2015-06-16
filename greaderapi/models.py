from django.contrib.auth.models import User
from django.db import models


class Token(models.Model):
	user=models.Foreignkey(User, db_index=True)
	token=models.CharField(max_length=255)
	expires=models.DateTimeField()

from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser,BaseUserManager

# class User(AbstractUser):
#     #  pass
#     name = models.CharField(max_length=200, null=True)
#     email = models.EmailField(unique=True, null=True)
#     bio = models.TimeField(null=True)
#     avatar = models.ImageField(null=True, default="avatar.svg")
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True, null=False)  # Ensure email is not null
    bio = models.TextField(null=True, blank=True)  # Corrected from TimeField
    avatar = models.ImageField(null=True, blank=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Add any other fields that are required

    objects = UserManager()

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) 
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
            ordering = ['-updated', '-created']
            
    def __str__(self):
        return self.body[0:50]
    


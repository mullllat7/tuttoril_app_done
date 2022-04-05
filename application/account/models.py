from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from tutor_root.settings import EMAIL_HOST_USER


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, *args, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, *args, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, primary_key=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def create_activation_code(self):
        from django.utils.crypto import get_random_string
        code = get_random_string(6, '0123456789')
        self.activation_code = code
        self.save()

    def activate_with_code(self, activation_code):
        if self.activation_code != activation_code:
            raise Exception('Неверный код, проверь и попробуй снова')
        self.is_active = True
        self.save()

    def send_activation_email(self):
        msg = f'''Спасибо за регистрацию,: 
        Вот ваш код активации:
                http://localhost:8000/auth/account/activate/{self.activation_code}/'''

        send_mail('Akkaunt aktivirovan', msg, EMAIL_HOST_USER, [self.email])

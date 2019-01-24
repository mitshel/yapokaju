from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        Group, Permission, PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.core.models import TimestampsMixin


# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email address must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


USER_EMAIL_UNIQUE_ERR = _("A user with that email address already exists.")


class User(TimestampsMixin, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), default='', unique=True,
                              error_messages={'unique': USER_EMAIL_UNIQUE_ERR})
    first_name = models.CharField(_('first name'), max_length=32, default='')
    last_name = models.CharField(_('last name'), max_length=32, default='')
    phone = models.CharField('номер телефона', max_length=32, default='', blank=True)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_(
                                        'Designates whether this user should be treated as active. '
                                        'Unselect this instead of deleting accounts.'))
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can '
                                               'log into this admin site.'))
    is_volunteer = models.BooleanField(_('volunteer status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name')

    class Meta(object):
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_full_name(self):
        """
        Returns the short name for the user.
        """
        return "{} {}".format(self.first_name, self.last_name)


class ProxyGroup(Group):
    """
    docstring for proxy ProxyGroup class.
    """
    class Meta(object):
        proxy = True

        verbose_name = _('group')
        verbose_name_plural = _('groups')
        default_permissions = ()


class ProxyPermission(Permission):
    """
    docstring for proxy ProxyPermission class.
    """

    class Meta(object):
        proxy = True

        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        default_permissions = ()

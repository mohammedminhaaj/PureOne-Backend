from typing import cast

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from .queryset import RestorableQuerySet, SoftDeleteQuerySet


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, mobile_number: str, password: str, **kwargs):
        if not mobile_number:
            raise ValueError("Users must have a mobile number")

        user = cast(AbstractBaseUser, self.model(
            mobile_number=mobile_number, **kwargs))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile_number: str, password: str, **kwargs):
        kwargs["is_superuser"] = False
        kwargs["is_staff"] = False
        return self._create_user(mobile_number, password, **kwargs)

    def create_superuser(self, mobile_number: str, password: str, **kwargs):
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have `is_superuser=True`")
        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have `is_staff=True`")

        return self._create_user(mobile_number, password, **kwargs)


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        """Retrieve models that are not 'soft-deleted'."""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class RestorableManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        """Retrieve all models with support for restoring deleted items."""
        return RestorableQuerySet(self.model, using=self._db)
    
class CartManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        """Retrieve all cart data whose products are not deleted"""
        return super().get_queryset().filter(product_quantity__product__deleted_at__isnull = True, product_quantity__quantity__grams__lte = models.F("product_quantity__product__available_quantity"))

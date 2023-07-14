
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class AuditedModel(models.Model):
    """Base model to define common properties for monitoring changes to models."""

    created_at = models.DateTimeField(verbose_name=_(
        "created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("created by"),
        related_name="%(app_label)s_%(class)s_created_by",
        blank=True,
        null=True,
        default=None,
        editable=False,
    )
    modified_at = models.DateTimeField(verbose_name=_(
        "modified at"), auto_now=True, editable=False)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("modified by"),
        related_name="%(app_label)s_%(class)s_modified_by",
        blank=True,
        null=True,
        default=None,
        editable=False,
    )

    def __str__(self) -> str:
        return (
            f"Created by {str(self.created_by)} at {self.created_at}, "
            f"Modified by {str(self.modified_by)} at {self.modified_at}"
        )

    def save(self, *args, **kwargs):
        user = kwargs.pop("current_user", None)
        if self.pk:
            self.modified_by = self.modified_by if self.modified_by and not user else user
            self.created_by = user if not self.created_by else self.created_by
        else:
            self.created_by = self.created_by if self.created_by and not user else user
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Base model to add soft deletion support to models."""

    deleted_at = models.DateTimeField(verbose_name=_(
        "deleted at"), blank=True, null=True, default=None, editable=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("deleted by"),
        related_name="%(app_label)s_%(class)s_deleted_by",
        blank=True,
        null=True,
        default=None,
        editable=False,
    )

    def delete(self, *args, **kwargs):
        """Perform soft-deletion by updating parameters."""
        current_user = kwargs.pop("current_user", None)
        self.deleted_at = now()
        self.deleted_by = self.deleted_by if self.deleted_by and not current_user else current_user
        super().save()

    def remove(self):
        """Delete data from the DB."""
        super().delete()

    def restore(self):
        """Undo the soft-delete for this instance."""
        self.deleted_at = None
        self.deleted_by = None
        super().save()

    class Meta:
        abstract = True


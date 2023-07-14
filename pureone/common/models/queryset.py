from django.db import models
from django.utils.timezone import now


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self, **kwargs) -> tuple[int, dict[str, int]]:
        current_user = kwargs.pop("current_user")
        count = self.update(deleted_at=now(), deleted_by=current_user)
        return count, {f"{self.model._meta.app_label}.{self.model.__name__}": count}

    def remove(self) -> tuple[int, dict[str, int]]:
        return super().delete()


class RestorableQuerySet(models.QuerySet):
    def restore(self) -> tuple[int, dict[str, int]]:
        count = self.update(deleted_at=None, deleted_by=None)
        return count, {f"{self.model._meta.app_label}.{self.model.__name__}": count}

    def mark_deleted(self, **kwargs) -> tuple[int, dict[str, int]]:
        current_user = kwargs.pop("current_user")
        count = self.update(deleted_at=now(), deleted_by=current_user)
        return count, {f"{self.model._meta.app_label}.{self.model.__name__}": count}

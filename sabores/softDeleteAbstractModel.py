from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Soft delete en lote"""
        return super().update(deleted_at=timezone.now())

    def restore(self):
        """Restaura en lote"""
        return super().update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        """Devuelve todos, incluidos eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Devuelve solo eliminados"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = SoftDeleteManager()      # solo activos
    all_objects = SoftDeleteManager()  # todos (activos + eliminados)

    class Meta:
        abstract = True

    # --- Métodos de instancia ---
    def delete(self, using=None, keep_parents=False):
        """Soft delete de instancia"""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restaura instancia eliminada"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

from django.db import models


class BaseModel(models.Model):
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    def __str__(self) -> str:
        if hasattr(self, 'name') and self.name:
            return self.name

        if hasattr(self, 'title') and self.title:
            return self.title

        return f"{self.__class__.__name__}::{str(self.pk)}"

    class Meta:
        abstract = True

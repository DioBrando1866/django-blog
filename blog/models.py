from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class UserManager(BaseUserManager):
    """Manager para un usuario que se identifica por email (como en Symfony)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Equivale a la entidad User de Symfony. ROLE_ADMIN -> is_staff."""

    username = None
    email = models.EmailField("email", max_length=180, unique=True)
    name = models.CharField(max_length=255)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Image(models.Model):
    """Imagen de la galería de la portada, asociada a una categoría."""

    file = models.ImageField(upload_to="gallery/")
    num_likes = models.PositiveIntegerField(default=0)
    num_views = models.PositiveIntegerField(default=0)
    num_downloads = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="images"
    )

    def __str__(self):
        return self.file.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    post_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    image = models.ImageField(upload_to="blog/")
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    num_likes = models.PositiveIntegerField(default=0)
    num_comments = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("single_post", kwargs={"slug": self.slug})

    def _unique_slug(self):
        base = slugify(self.title)[:240] or "post"
        slug, n = base, 2
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)


class Comment(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    text = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return f"{self.name} on {self.post}"


class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.subject} ({self.email})"

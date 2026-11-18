from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import Category, Comment, Contact, Image, Post, User


class BootstrapFormMixin:
    """Añade la clase `form-control` de Bootstrap 3 a los campos de texto."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.FileInput)):
                continue
            css = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{css} form-control".strip()


class ImageTypeMixin:
    """Solo permite JPEG y PNG (igual que la restricción de Symfony)."""

    allowed_formats = ("JPEG", "PNG")

    def _check_image(self, upload):
        # Tras ImageField.clean(), un fichero recién subido trae el objeto PIL en `.image`
        pil_image = getattr(upload, "image", None)
        if pil_image is not None and pil_image.format not in self.allowed_formats:
            raise forms.ValidationError("Please upload a valid image file")
        return upload


class RegistrationForm(BootstrapFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    agree_terms = forms.BooleanField(
        label="Agree terms",
        error_messages={"required": "You should agree to our terms."},
    )

    class Meta:
        model = User
        fields = ("email", "name")
        error_messages = {
            "email": {"unique": "There is already an account with this email"},
        }

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class PostForm(ImageTypeMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "image")
        widgets = {"content": forms.Textarea(attrs={"rows": 4})}

    def clean_image(self):
        return self._check_image(self.cleaned_data["image"])


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("name", "email", "text")
        labels = {"text": "Type Your Comment"}


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("first_name", "last_name", "email", "subject", "message")
        error_messages = {
            "first_name": {"required": "Field `First Name` is mandatory"},
            "email": {"required": "Field `email` is mandatory"},
        }


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)


class GalleryImageForm(ImageTypeMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Image
        fields = ("file", "num_likes", "num_views", "num_downloads", "category")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # En Symfony la categoría era obligatoria en este formulario
        self.fields["category"].required = True

    def clean_file(self):
        return self._check_image(self.cleaned_data["file"])

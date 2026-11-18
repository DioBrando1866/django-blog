from functools import wraps

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CategoryForm,
    CommentForm,
    ContactForm,
    GalleryImageForm,
    PostForm,
    RegistrationForm,
)
from .models import Category, Image, Post


def admin_required(view):
    """Equivale a #[IsGranted('ROLE_ADMIN')]: exige login y ser staff."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return login_required(wrapper)


def recent_posts():
    return Post.objects.select_related("post_user")[:5]


# --------------------------------------------------------------- páginas ---
@login_required
def index(request):
    categories = Category.objects.prefetch_related("images")
    return render(request, "index.html", {"categories": categories})


@login_required
def about(request):
    return render(request, "about.html")


@login_required
def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("thankyou")
    return render(request, "contact.html", {"form": form})


def thankyou(request):
    return render(request, "thankyou.html")


# ------------------------------------------------------------------ blog ---
@login_required
def blog_list(request):
    """Listado paginado. Con ?searchTerm=... filtra por título o contenido."""
    term = request.GET.get("searchTerm", "").strip()
    posts = Post.objects.select_related("post_user")
    if term:
        posts = posts.filter(Q(title__icontains=term) | Q(content__icontains=term))

    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    # get_page() corrige páginas inválidas (equivale a redirigir a la última)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_range = list(
        paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    )

    return render(
        request,
        "blog.html",
        {
            "posts": page_obj,
            "page_obj": page_obj,
            "page_range": page_range,
            "ellipsis": Paginator.ELLIPSIS,
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "progress": round(page_obj.number / paginator.num_pages * 100),
            "search_term": term,
            "recents": recent_posts(),
        },
    )


def single_post(request, slug):
    post = get_object_or_404(Post.objects.select_related("post_user"), slug=slug)

    form = CommentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        Post.objects.filter(pk=post.pk).update(num_comments=F("num_comments") + 1)
        return redirect(post)

    return render(
        request,
        "blog/single_post.html",
        {
            "post": post,
            "recents": recent_posts(),
            "recent_comments": post.comments.all()[:5],
            "comment_form": form,
        },
    )


@require_POST
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    Post.objects.filter(pk=post.pk).update(num_likes=F("num_likes") + 1)
    post.refresh_from_db(fields=["num_likes"])
    return JsonResponse({"success": True, "likes": post.num_likes})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.post_user = request.user  # slug y contadores se rellenan solos
        post.save()
        return redirect(post)
    return render(request, "blog/new_post.html", {"form": form})


# ------------------------------------------------------ registro / login ---
def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "registration/register.html", {"form": form})


# ----------------------------------------------------------------- admin ---
@admin_required
def admin_images(request):
    form = GalleryImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("app_images")
    images = Image.objects.select_related("category")
    return render(request, "panel/images.html", {"form": form, "images": images})


@admin_required
def admin_categories(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("app_categories")
    return render(
        request,
        "panel/categories.html",
        {"form": form, "categories": Category.objects.all()},
    )

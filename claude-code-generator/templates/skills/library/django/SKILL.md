---
name: django
description: Expert knowledge in Django web framework including models, views, ORM, authentication, Django REST Framework, and production deployment best practices.
allowed-tools: [Read, Write, Edit, Bash]
---

# Django Skill

Comprehensive guide for building robust web applications and REST APIs with Django.

## Quick Start

### Project Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Django
pip install django

# Create project
django-admin startproject myproject
cd myproject

# Create app
python manage.py startapp myapp

# Run development server
python manage.py runserver
```

### Basic Configuration

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # Add your app
]

# Database (default SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```python
# urls.py (project level)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
]
```

---

## Models

### Basic Model

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
```

### Model Relationships

```python
# One-to-One
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(blank=True)

# Many-to-Many
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Post(models.Model):
    # ... other fields
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

# Many-to-Many with through table
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    date_joined = models.DateField()
    role = models.CharField(max_length=50)

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, through=Membership)
```

### Model Methods

```python
class Post(models.Model):
    # ... fields

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == 'published' and self.published_at is not None

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    @classmethod
    def published_posts(cls):
        return cls.objects.filter(status='published')
```

---

## Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Revert migration
python manage.py migrate myapp 0002

# Create empty migration
python manage.py makemigrations --empty myapp

# SQL for migration
python manage.py sqlmigrate myapp 0001
```

### Custom Migration

```python
# migrations/0003_custom_migration.py
from django.db import migrations

def populate_categories(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    categories = [
        {'name': 'Technology', 'slug': 'technology'},
        {'name': 'Business', 'slug': 'business'},
    ]
    for cat in categories:
        Category.objects.create(**cat)

def reverse_populate(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    Category.objects.filter(slug__in=['technology', 'business']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0002_previous_migration'),
    ]

    operations = [
        migrations.RunPython(populate_categories, reverse_populate),
    ]
```

---

## Django ORM

### Query Basics

```python
# Get all
posts = Post.objects.all()

# Filter
published_posts = Post.objects.filter(status='published')
tech_posts = Post.objects.filter(category__name='Technology')

# Exclude
non_draft_posts = Post.objects.exclude(status='draft')

# Get single object
post = Post.objects.get(id=1)
post = Post.objects.get(slug='my-post')

# Get or 404
from django.shortcuts import get_object_or_404
post = get_object_or_404(Post, slug='my-post')

# First/Last
first_post = Post.objects.first()
last_post = Post.objects.last()

# Exists
has_posts = Post.objects.filter(author=user).exists()

# Count
post_count = Post.objects.count()
```

### Complex Queries

```python
from django.db.models import Q, F, Count, Avg, Sum, Max, Min

# Q objects (OR queries)
posts = Post.objects.filter(
    Q(category__name='Technology') | Q(category__name='Science')
)

# NOT queries
posts = Post.objects.filter(~Q(status='draft'))

# Complex Q
posts = Post.objects.filter(
    Q(status='published') &
    (Q(category__name='Tech') | Q(tags__name='Python'))
)

# F expressions (compare fields)
posts = Post.objects.filter(views__gt=F('likes') * 2)

# Update with F
Post.objects.filter(id=1).update(views=F('views') + 1)

# Aggregation
from django.db.models import Count, Avg

stats = Post.objects.aggregate(
    total=Count('id'),
    avg_views=Avg('views'),
    max_views=Max('views')
)
# Returns: {'total': 100, 'avg_views': 523.5, 'max_views': 1500}

# Annotate (per-object aggregation)
categories = Category.objects.annotate(
    post_count=Count('posts'),
    avg_views=Avg('posts__views')
)

for cat in categories:
    print(f"{cat.name}: {cat.post_count} posts, {cat.avg_views} avg views")
```

### Select Related / Prefetch Related

```python
# select_related (ForeignKey, OneToOne) - SQL JOIN
posts = Post.objects.select_related('author', 'category').all()

# prefetch_related (ManyToMany, reverse ForeignKey) - Separate queries
posts = Post.objects.prefetch_related('tags', 'comments').all()

# Combined
posts = Post.objects.select_related('author', 'category').prefetch_related('tags')

# Custom prefetch
from django.db.models import Prefetch

posts = Post.objects.prefetch_related(
    Prefetch('comments', queryset=Comment.objects.filter(is_approved=True))
)
```

### Raw SQL

```python
# Raw queries
posts = Post.objects.raw('SELECT * FROM myapp_post WHERE status = %s', ['published'])

# Execute custom SQL
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("UPDATE myapp_post SET views = views + 1 WHERE id = %s", [post_id])
    cursor.execute("SELECT * FROM myapp_post WHERE status = %s", ['published'])
    rows = cursor.fetchall()
```

---

## Views

### Function-Based Views

```python
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Post
from .forms import PostForm

def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')

    context = {
        'posts': posts
    }
    return render(request, 'posts/list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.increment_views()

    context = {
        'post': post
    }
    return render(request, 'posts/detail.html', context)

def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post-detail', slug=post.slug)
    else:
        form = PostForm()

    return render(request, 'posts/form.html', {'form': form})

def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post-detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/form.html', {'form': form, 'post': post})

def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        post.delete()
        return redirect('post-list')

    return render(request, 'posts/confirm_delete.html', {'post': post})

# JSON response
def post_api(request):
    posts = Post.objects.values('id', 'title', 'slug')
    return JsonResponse(list(posts), safe=False)
```

### Class-Based Views

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category')

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def get_object(self):
        obj = super().get_object()
        obj.increment_views()
        return obj

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/form.html'

    def get_queryset(self):
        # Only allow editing own posts
        return Post.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
```

---

## URLs

```python
# urls.py
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Function-based views
    path('', views.post_list, name='list'),
    path('<slug:slug>/', views.post_detail, name='detail'),
    path('create/', views.post_create, name='create'),
    path('<slug:slug>/edit/', views.post_update, name='update'),
    path('<slug:slug>/delete/', views.post_delete, name='delete'),

    # Class-based views
    path('', views.PostListView.as_view(), name='list'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='detail'),
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('<slug:slug>/edit/', views.PostUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='delete'),

    # URL with regex
    path('posts/<int:year>/<int:month>/', views.posts_by_date, name='by-date'),
]
```

---

## Forms

### Model Forms

```python
# forms.py
from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'status', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters')
        return title

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        content = cleaned_data.get('content')

        if status == 'published' and len(content) < 100:
            raise forms.ValidationError('Published posts must have at least 100 characters')

        return cleaned_data
```

### Regular Forms

```python
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@example.com'):
            raise forms.ValidationError('Must use company email')
        return email

    def send_email(self):
        # Send email logic
        pass

# View
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send_email()
            return redirect('success')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
```

---

## Authentication

### Built-in Authentication

```python
# views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'profile.html')

# settings.py
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

### Custom User Model

```python
# models.py
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

# settings.py
AUTH_USER_MODEL = 'myapp.CustomUser'
```

### Permissions

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

@login_required
@permission_required('myapp.delete_post', raise_exception=True)
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    return redirect('post-list')

# Class-based view
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'myapp.delete_post'
    model = Post

# Check in code
if request.user.has_perm('myapp.delete_post'):
    # Allow delete
    pass

# Custom permission
class Post(models.Model):
    # ... fields

    class Meta:
        permissions = [
            ('can_publish', 'Can publish posts'),
            ('can_feature', 'Can feature posts'),
        ]
```

---

## Django REST Framework

### Installation

```bash
pip install djangorestframework
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

### Serializers

```python
# serializers.py
from rest_framework import serializers
from .models import Post, Category, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['author']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'author_name',
            'category', 'category_name', 'content', 'status',
            'published_at', 'created_at', 'views',
            'comments', 'comment_count'
        ]
        read_only_fields = ['author', 'views', 'created_at']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title too short')
        return value
```

### API Views

```python
# views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'views']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        return queryset.select_related('author', 'category').prefetch_related('comments')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        post = self.get_object()
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        return Response({'status': 'published'})

    @action(detail=False, methods=['get'])
    def popular(self, request):
        posts = self.get_queryset().order_by('-views')[:10]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = router.urls
```

### Authentication

```python
# Token authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Create tokens for users
from rest_framework.authtoken.models import Token

token = Token.objects.create(user=user)
print(token.key)

# API view for login
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/login/', obtain_auth_token),
]

# Custom login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    return Response({'error': 'Invalid credentials'}, status=401)
```

---

## Testing

```python
# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Post, Category

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Tech', slug='tech')

    def test_post_creation(self):
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            category=self.category,
            content='Test content',
            status='published'
        )

        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(str(post), 'Test Post')

    def test_post_slug_generation(self):
        post = Post(title='My Test Post', author=self.user, content='Content')
        post.save()

        self.assertEqual(post.slug, 'my-test-post')

class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            category=self.category,
            content='Test content',
            status='published'
        )

    def test_post_list_view(self):
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_detail_view(self):
        response = self.client.get(f'/posts/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_create_requires_login(self):
        response = self.client.get('/posts/create/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_post_create_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post('/posts/create/', {
            'title': 'New Post',
            'content': 'New content',
            'category': self.category.id,
            'status': 'draft'
        })

        self.assertEqual(Post.objects.count(), 2)

# Run tests
# python manage.py test
```

---

## Admin Interface

```python
# admin.py
from django.contrib import admin
from .models import Post, Category, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author', 'content', 'is_approved']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'views']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-published_at']
    inlines = [CommentInline]

    fieldsets = [
        ('Content', {
            'fields': ['title', 'slug', 'content', 'author', 'category', 'tags']
        }),
        ('Status', {
            'fields': ['status', 'published_at']
        }),
        ('Metadata', {
            'fields': ['views'],
            'classes': ['collapse']
        }),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author', 'category')
```

---

## Production Best Practices

### Settings Organization

```python
# settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = []

# settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.development')
```

### Static Files

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Collect static files
# python manage.py collectstatic
```

### Deployment

```python
# requirements.txt
Django==4.2
psycopg2-binary
gunicorn
whitenoise
django-environ

# Procfile (Heroku)
web: gunicorn myproject.wsgi

# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.production')
application = get_wsgi_application()
```

---

## Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django Best Practices: https://django-best-practices.readthedocs.io/
- Two Scoops of Django: https://www.feldroy.com/books/two-scoops-of-django-3-x
- Django Packages: https://djangopackages.org/

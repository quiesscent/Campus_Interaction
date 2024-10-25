
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, ResourceUploadForm, CommentForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Resource, Category, Comment
from django.db.models import F

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'resources/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'resources/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    user_resources = Resource.objects.filter(uploaded_by=request.user)
    return render(request, 'resources/dashboard.html', {
        'user_resources': user_resources
    })

def view_resources(request):
    category = request.GET.get('category')
    search_query = request.GET.get('search')
    resource_type = request.GET.get('type')
    
    resources = Resource.objects.filter(is_approved=True)
    
    if category:
        resources = resources.filter(category__name=category)
    if search_query:
        resources = resources.filter(title__icontains=search_query)
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
        
    paginator = Paginator(resources, 12)  # Show 12 resources per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'resources/view_resources.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
        'resource_type': resource_type
    })

@login_required
def upload_resource(request):
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource uploaded successfully!')
            return redirect('dashboard')
    else:
        form = ResourceUploadForm()
    
    return render(request, 'resources/upload_resources.html', {'form': form})

@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    Resource.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    
    # Get related resources (same category)
    related_resources = Resource.objects.filter(
        category=resource.category,
        is_approved=True
    ).exclude(pk=pk)[:5]  # Show up to 5 related resources
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.resource = resource
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('resource_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    comments = resource.comments.all().order_by('-created_at')
    
    return render(request, 'resources/resource_detail.html', {
        'resource': resource,
        'comments': comments,
        'comment_form': comment_form,
        'related_resources': related_resources
    })

def home(request):
    recent_resources = Resource.objects.filter(is_approved=True).order_by('-date_uploaded')[:6]
    popular_resources = Resource.objects.filter(is_approved=True).order_by('-views_count')[:6]
    categories = Category.objects.all()
    
    return render(request, 'resources/home.html', {
        'recent_resources': recent_resources,
        'popular_resources': popular_resources,
        'categories': categories
    })

@login_required
def add_comment(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                resource=resource,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty!')
    return redirect('resource_detail', pk=pk)

@login_required
def report_resource(request, pk):
    if request.method == 'POST':
        resource = get_object_or_404(Resource, pk=pk)
        reason = request.POST.get('reason')
        details = request.POST.get('details')
        # Add your report handling logic here
        messages.success(request, 'Resource reported successfully. Our team will review it.')
    return redirect('resource_detail', pk=pk)

@login_required
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.user != resource.uploaded_by and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this resource.')
        return redirect('resource_detail', pk=pk)
        
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('resource_detail', pk=pk)
    else:
        form = ResourceUploadForm(instance=resource)
    
    return render(request, 'resources/upload_resources.html', {
        'form': form,
        'is_edit': True,
        'resource': resource
    })

@login_required
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.user != resource.uploaded_by and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this resource.')
        return redirect('resource_detail', pk=pk)
        
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully.')
        return redirect('dashboard')
    
    return redirect('resource_detail', pk=pk)
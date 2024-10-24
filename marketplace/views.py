from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, UserRating, Category, SearchHistory
from .forms import ItemForm, RatingForm
from django.shortcuts import render
from django.db.models import Q  # Import Q for complex queries
from .models import Item
from django.contrib import messages 
from django.db.models import F 
from django.contrib.auth.decorators import login_required


def item_list(request):
    query = request.GET.get('q')
    category_name = request.GET.get('category', 'all')  # Default to 'all' if no category is selected

    # Start with all items
    items = Item.objects.all()

    # Filter items based on the search query in title or description
    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Filter by category name if specified and not "all"
    if category_name and category_name != "all":
        items = items.filter(category__name__iexact=category_name)

    # Get all categories for the dropdown menu
    categories = Category.objects.all()

    # Initialize search history and search items
    search_items = []
    if request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')

        # Create a list of tuples (search_history, item) for each search
        for search in search_history:
            # Look for an item that matches the search query
            item = items.filter(title__iexact=search.query).first()
            search_items.append((search, item))

    # Create a dictionary to categorize items by category
    categorized_items = {}
    for category in categories:  # Ensure we iterate over all categories
        categorized_items[category.name] = items.filter(category=category)
    deal_items = Item.objects.filter(price__lt=F('original_price'))

    return render(request, 'marketplace/item_list.html', {
        'categorized_items': categorized_items,  # Pass the categorized items
        'query': query,
        'categories': categories,
        'selected_category': category_name,
        'search_items': search_items,  # Pass the matched items
        'user': request.user,
        'deal_items': deal_items,
    })


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # Initialize form
    form = RatingForm()

    if request.method == 'POST' and request.user.is_authenticated:
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')  # Capture comment if needed
        form = RatingForm(request.POST)  # Create a form instance with POST data

        # Check if the form is valid and stars rating is provided
        if form.is_valid() and stars:
            # Create or update the user rating
            user_rating, created = UserRating.objects.get_or_create(
                item=item,
                user=request.user,
                defaults={'stars': stars, 'comment': comment}  # Create if not exists
            )

            if not created: 
                # Update existing rating
                user_rating.stars = stars
                user_rating.comment = comment  
                user_rating.save()

            # Redirect to the same item detail page after saving
            return redirect('item_detail', item_id=item.id)

    # Create a new search history entry with the item title regardless of the source
    if request.user.is_authenticated:
        SearchHistory.objects.get_or_create(user=request.user, query=item.title)

    return render(request, 'marketplace/item_detail.html', {
        'item': item,
        'form': form,
        'average_rating': item.average_rating
    })
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'marketplace/add_item.html', {'form': form})


def seller_dashboard(request):
    if request.user.is_authenticated:
        user_items = Item.objects.filter(seller=request.user)

        if request.method == 'POST':
            item_id = request.POST.get('item_id')
            new_price = request.POST.get('new_price')
            item = get_object_or_404(Item, id=item_id, seller=request.user)

            # Update price
            if new_price:
                item.original_price = item.price  # Set the current price as the original price
                item.price = new_price
                item.save()
                messages.success(request, f"Price for {item.title} updated successfully.")
                return redirect('seller_dashboard')

        return render(request, 'marketplace/seller_dashboard.html', {
            'user_items': user_items,
        })
    else:
        return redirect('login')

def mark_as_sold(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST' and request.user == item.seller:
        item.sold = True
        item.save()
        messages.success(request, "Item marked as sold.")
        return redirect('seller_dashboard')
    return redirect('item_detail', item_id=item.id)

def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST' and request.user == item.seller:
        item.delete()
        messages.success(request, "Item deleted.")
        if not Item.objects.filter(seller=request.user).exists():
            return redirect('item_list')  

        return redirect('seller_dashboard') 

    return redirect('item_detail', item_id=item.id)
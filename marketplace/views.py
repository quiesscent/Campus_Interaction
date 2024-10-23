from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, UserRating
from .forms import ItemForm, RatingForm

def item_list(request):
    items = Item.objects.all()
    return render(request, 'marketplace/item_list.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')  # Capture comment if needed
        form = RatingForm(request.POST)  # Ensure you're using the correct form

        if form.is_valid() and stars:
            # Check if the user has already rated this item
            user_rating, created = UserRating.objects.get_or_create(
                item=item,
                user=request.user,
                defaults={'stars': stars, 'comment': comment}  # Create if not exists
            )

            if not created:  # If the rating already exists, update it
                user_rating.stars = stars
                user_rating.comment = comment  # Update comment if needed
                user_rating.save()
            
            return redirect('item_detail', item_id=item.id)
    else:
        form = RatingForm()

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

document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('likeButton');
    if (likeButton) {
        likeButton.addEventListener('click', function() {
            const resourceId = this.dataset.resourceId;
            fetch(`/resources/${resourceId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    this.querySelector('i').classList.replace('fa-heart-o', 'fa-heart');
                } else {
                    this.querySelector('i').classList.replace('fa-heart', 'fa-heart-o');
                }
            });
        });
    }
});
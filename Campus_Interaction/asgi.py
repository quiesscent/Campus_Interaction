import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Campus_Interaction.settings')

# Get the Django ASGI application early to ensure the AppRegistry is populated
# before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import these after the Django ASGI application is created
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import messaging.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messaging.routing.websocket_urlpatterns
        )
    ),
})
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enfund.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter(
    #             routing.websocket_urlpatterns
    #         )
    #     )
    # ),
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})
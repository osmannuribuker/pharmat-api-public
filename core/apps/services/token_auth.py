from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
import re
from channels.db import database_sync_to_async
from rest_framework.permissions import IsAuthenticated
import requests
from core.apps.authentication.models import User
from rest_framework_simplejwt.backends import TokenBackend

@database_sync_to_async
def get_user(token_key,user_id):
    try:
        valid_data = TokenBackend(algorithm='HS256').decode(token_key,verify=False)
        print(token_key)
        print(valid_data)
        user = valid_data['user_id']
        print(user, user_id, token_key)
        if user == int(user_id):
            return User.objects.get(id=user)
        else: 
            raise
    except Exception as e:
        print(e)
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        path = scope['path']
        if b'authorization' in headers[b"cookie"]:
            cookies = headers[b"cookie"].decode()
            token_key = re.search("authorization=(.*)(; )?", cookies).group(1)
            user_id = path.replace("/ws/pharmacy/", "")
            scope['user'] = await get_user(token_key, user_id)
        return await self.inner(scope, receive, send)


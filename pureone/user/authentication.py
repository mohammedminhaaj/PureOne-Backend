from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner, keyword="token"):
        self.keyword = keyword
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = dict(kv.split("=") for kv in query_string.split("&") if kv)
        token = query_params.get(self.keyword)
        
        if token:
            user = await self.get_user_from_token(token)
            if user is not None:
                scope["user"] = user
        
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            return Token.objects.select_related("user").get(key=token).user
        except Exception:
            return AnonymousUser()

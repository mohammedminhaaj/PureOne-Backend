from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()
            self.user_group_name = f"user_{self.scope['user'].id}_order_list"
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)  

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        await self.channel_layer.group_send(self.user_group_name, message)

    async def order_status(self, event):
        data = json.dumps(event)
        await self.send(text_data=data)



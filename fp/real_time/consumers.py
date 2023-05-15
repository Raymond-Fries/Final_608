import json
from channels.generic.websocket import AsyncWebsocketConsumer


class real_time_consumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add('real_time_data',self.channel_name)
        await self.accept()

    async def disconnect(self,code):

        await self.channel_layer.group_discard(
            'real_time_data',
            self.channel_name)

    async def intraday_message(self,event):
        message = event

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def transaction_message(self,event):
        message = event

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def position_message(self,event):
        message = event

        await self.send(text_data=json.dumps({
            'message': message
        }))
    async def account_message(self,event):
        message = event

        await self.send(text_data=json.dumps({
            'message': message
        }))

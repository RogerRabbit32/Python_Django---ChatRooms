import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PrivateChat, Message
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the chat ID from the URL or request parameters
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = "chat_%s" % self.chat_id
        # Check if the user is authorized to access the chat
        chat = await self.get_chat(self.chat_id)
        if not chat:
            await self.close()
            return

        # Add the user to the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the chat group
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        chat = await self.get_chat(self.chat_id)
        if chat:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Parse the received message
        message_data = self.parse_message(text_data)

        # Get the chat ID from the URL or request parameters
        chat_id = self.scope['url_route']['kwargs']['chat_id']

        # Check if the user is authorized to access the chat
        chat = await self.get_chat(chat_id)
        if not chat:
            await self.close()
            return

        # Create and save the message to the database
        message = await self.create_message(chat, message_data)

        # Serialize the message
        serialized_message = MessageSerializer(message).data

        # Broadcast the message to all connected clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': serialized_message
            }
        )

    async def chat_message(self, event):
        # Send the received chat message to the client
        message = event['message']
        await self.send(text_data=json.dumps({"message": message}))
        # await self.send(text_data=message['text'])

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            chat = PrivateChat.objects.get(id=chat_id)
            if self.scope["user"] == chat.user1 or self.scope["user"] == chat.user2:
                return chat
        except PrivateChat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, chat, message_data):
        message = Message.objects.create(
            content_object=chat,
            sender=self.scope['user'],
            text=message_data['message']
        )
        return message

    def parse_message(self, text_data):
        # Parse the received message data (adjust as per your message format)
        message_data = json.loads(text_data)
        return message_data

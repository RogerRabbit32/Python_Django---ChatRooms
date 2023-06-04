import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PrivateChat, ChatRoom, Message
from api.serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the chat ID or public chat ID from the URL or request parameters
        self.chat_id = self.scope['url_route']['kwargs'].get('chat_id')
        self.public_chat_id = self.scope['url_route']['kwargs'].get('public_chat_id')

        # Check if the user is authorized to access the chat
        chat = await self.get_private_chat(self.chat_id)
        public_chat = await self.get_public_chat(self.public_chat_id)

        if not chat and not public_chat:
            await self.close()
            return

        # Determine the room group name based on the chat type
        if chat:
            self.room_group_name = f"private_chat_{self.chat_id}"
        elif public_chat:
            self.room_group_name = f"public_chat_{self.public_chat_id}"

        # Add the user to the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the chat group
        if self.chat_id:
            await self.channel_layer.group_discard(
                f"private_chat_{self.chat_id}",
                self.channel_name
            )
        else:
            await self.channel_layer.group_discard(
                f"public_chat_{self.public_chat_id}",
                self.channel_name
            )

    async def receive(self, text_data):
        # Parse the received message
        message_data = self.parse_message(text_data)

        if self.chat_id:
            # Handle private chat
            chat = await self.get_private_chat(self.chat_id)
        elif self.public_chat_id:
            # Handle public chat
            chat = await self.get_public_chat(self.public_chat_id)

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
    def get_private_chat(self, chat_id):
        try:
            chat = PrivateChat.objects.get(id=chat_id)
            if self.scope["user"] == chat.user1 or self.scope["user"] == chat.user2:
                return chat
        except PrivateChat.DoesNotExist:
            return None

    @database_sync_to_async
    def get_public_chat(self, chat_id):
        try:
            chat = ChatRoom.objects.get(id=chat_id)
            if self.scope["user"] == chat.owner or self.scope["user"] in chat.chat_users.all():
                return chat
        except ChatRoom.DoesNotExist:
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
        message_data = json.loads(text_data)
        return message_data


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Get the chat ID from the URL or request parameters
#         self.chat_id = self.scope['url_route']['kwargs']['chat_id']
#         self.room_group_name = "chat_%s" % self.chat_id
#         # Check if the user is authorized to access the chat
#         chat = await self.get_chat(self.chat_id)
#         if not chat:
#             await self.close()
#             return
#
#         # Add the user to the chat group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         # Accept the WebSocket connection
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Remove the user from the chat group
#         self.chat_id = self.scope['url_route']['kwargs']['chat_id']
#         chat = await self.get_chat(self.chat_id)
#         if chat:
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )
#
#     async def receive(self, text_data):
#         # Parse the received message
#         message_data = self.parse_message(text_data)
#
#         # Get the chat ID from the URL or request parameters
#         chat_id = self.scope['url_route']['kwargs']['chat_id']
#
#         # Check if the user is authorized to access the chat
#         chat = await self.get_chat(chat_id)
#         if not chat:
#             await self.close()
#             return
#
#         # Create and save the message to the database
#         message = await self.create_message(chat, message_data)
#
#         # Serialize the message
#         serialized_message = MessageSerializer(message).data
#
#         # Broadcast the message to all connected clients
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': serialized_message
#             }
#         )
#
#     async def chat_message(self, event):
#         # Send the received chat message to the client
#         message = event['message']
#         await self.send(text_data=json.dumps({"message": message}))
#         # await self.send(text_data=message['text'])
#
#     @database_sync_to_async
#     def get_chat(self, chat_id):
#         try:
#             chat = PrivateChat.objects.get(id=chat_id)
#             if self.scope["user"] == chat.user1 or self.scope["user"] == chat.user2:
#                 return chat
#         except PrivateChat.DoesNotExist:
#             return None
#
#     @database_sync_to_async
#     def create_message(self, chat, message_data):
#         message = Message.objects.create(
#             content_object=chat,
#             sender=self.scope['user'],
#             text=message_data['message']
#         )
#         return message
#
#     def parse_message(self, text_data):
#         # Parse the received message data (adjust as per your message format)
#         message_data = json.loads(text_data)
#         return message_data

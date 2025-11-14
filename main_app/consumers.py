import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        print(f"🔌 WebSocket connection attempt - Room: {self.room_id}, User: {self.user.username if self.user.is_authenticated else 'Anonymous'}")

        # Check if user is authenticated and part of this room
        if not self.user.is_authenticated:
            print(f"❌ User not authenticated, closing connection")
            await self.close()
            return

        # Verify user is part of this room
        is_valid = await self.is_user_in_room(self.user, self.room_id)
        if not is_valid:
            print(f"❌ User {self.user.username} not authorized for room {self.room_id}, closing connection")
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ WebSocket connection accepted - Room: {self.room_id}, User: {self.user.username}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # Note: Actual message saving is handled by the view
            # This can be used for typing indicators or other real-time features
        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        # Send message to WebSocket
        message_data = {
            "type": "new_message",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_first_name": event.get("sender_first_name", ""),
            "sender_last_name": event.get("sender_last_name", ""),
            "recipient_id": event["recipient_id"],
            "timestamp": event.get("timestamp", ""),
            "chat_id": event.get("chat_id"),
            "room_id": self.room_id  # Include room_id to verify message belongs to current room
        }
        print(f"📤 Sending message via WebSocket to room {self.room_id}: {message_data}")
        await self.send(text_data=json.dumps(message_data))

    async def message_read(self, event):
        # Notify that a message was read
        await self.send(text_data=json.dumps({
            "type": "message_read",
            "chat_id": event.get("chat_id")
        }))

    @database_sync_to_async
    def is_user_in_room(self, user, room_id):
        from .models import ChatRoom
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.initiator == user or room.receiver == user
        except ChatRoom.DoesNotExist:
            return False

class AlertsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group = "alerts_staff"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def alert_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "alert",
            "title": event.get("title"),
            "message": event.get("message"),
            "payload": event.get("payload", {})
        }))

class PCNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for PC notifications (session warnings, etc.)"""
    async def connect(self):
        # Get PC name from query string
        query_string = self.scope.get("query_string", b"").decode()
        pc_name = None
        
        # Parse query string
        if query_string:
            params = {}
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
            pc_name = params.get("pc_name", "")
        
        if not pc_name:
            print(f"❌ PC Notification WebSocket: No PC name provided")
            await self.close()
            return
        
        self.pc_name = pc_name
        self.group = f"pc_notifications_{pc_name}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        print(f"✅ PC Notification WebSocket connected: {pc_name}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)
        print(f"❌ PC Notification WebSocket disconnected: {getattr(self, 'pc_name', 'unknown')}")

    async def receive(self, text_data):
        # PC can send heartbeat or status updates
        try:
            data = json.loads(text_data)
            if data.get("type") == "heartbeat":
                await self.send(text_data=json.dumps({"type": "heartbeat_ack"}))
        except json.JSONDecodeError:
            pass

    async def session_warning(self, event):
        """Send session warning notification to PC"""
        message_data = {
            "type": "session_warning",
            "message": event.get("message", "Your session is about to end"),
            "minutes_left": event.get("minutes_left", 5),
            "end_time": event.get("end_time"),
            "booking_id": event.get("booking_id"),
            "pc_name": event.get("pc_name"),
            "show_popup": event.get("show_popup", True)
        }
        print(f"📤 PCNotificationConsumer: Sending session warning to {self.pc_name}")
        print(f"   Connected PC name: {self.pc_name}")
        print(f"   Event PC name: {event.get('pc_name')}")
        print(f"   Message data: {message_data}")
        print(f"   JSON: {json.dumps(message_data)}")
        try:
            await self.send(text_data=json.dumps(message_data))
            print(f"✅ Message sent successfully to {self.pc_name}")
        except Exception as e:
            print(f"❌ Error sending message to {self.pc_name}: {e}")
            import traceback
            traceback.print_exc()

class BookingStatusConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for booking status updates (for students and faculty)"""
    async def connect(self):
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            print(f"❌ BookingStatusConsumer: User not authenticated, closing connection")
            await self.close()
            return
        
        # Create a group for this user's booking updates
        self.group = f"booking_updates_{self.user.id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        print(f"✅ BookingStatusConsumer: User {self.user.username} (ID: {self.user.id}) connected")

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)
        print(f"❌ BookingStatusConsumer: User {getattr(self.user, 'username', 'unknown')} disconnected")

    async def receive(self, text_data):
        # Users can send heartbeat or other messages
        try:
            data = json.loads(text_data)
            if data.get("type") == "heartbeat":
                await self.send(text_data=json.dumps({"type": "heartbeat_ack"}))
        except json.JSONDecodeError:
            pass

    async def booking_status_update(self, event):
        """Send booking status update to user"""
        message_data = {
            "type": "booking_status_update",
            "booking_id": event.get("booking_id"),
            "status": event.get("status"),
            "message": event.get("message", "Your booking status has been updated"),
            "pc_name": event.get("pc_name", ""),
        }
        print(f"📤 BookingStatusConsumer: Sending booking update to user {self.user.username}")
        print(f"   Booking ID: {event.get('booking_id')}, Status: {event.get('status')}")
        try:
            await self.send(text_data=json.dumps(message_data))
            print(f"✅ Booking status update sent successfully")
        except Exception as e:
            print(f"❌ Error sending booking status update: {e}")
            import traceback
            traceback.print_exc()

class PCStatusBroadcastConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for broadcasting PC status updates to all users"""
    async def connect(self):
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            print(f"❌ PCStatusBroadcastConsumer: User not authenticated, closing connection")
            await self.close()
            return
        
        # Join the global PC status broadcast group
        self.group = "pc_status_updates"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        print(f"✅ PCStatusBroadcastConsumer: User {self.user.username} (ID: {self.user.id}) connected")

    async def disconnect(self, close_code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)
        print(f"❌ PCStatusBroadcastConsumer: User {getattr(self.user, 'username', 'unknown')} disconnected")

    async def receive(self, text_data):
        # Users can send heartbeat or other messages
        try:
            data = json.loads(text_data)
            if data.get("type") == "heartbeat":
                await self.send(text_data=json.dumps({"type": "heartbeat_ack"}))
        except json.JSONDecodeError:
            pass

    async def pc_status_update(self, event):
        """Broadcast PC status update to all connected users"""
        message_data = {
            "type": "pc_status_update",
            "pc_id": event.get("pc_id"),
            "pc_name": event.get("pc_name", ""),
            "booking_status": event.get("booking_status", "available"),
            "status": event.get("status", "connected"),  # connected/disconnected
            "system_condition": event.get("system_condition", "active"),  # active/repair
            "message": event.get("message", ""),
            "available_pcs_count": event.get("available_pcs_count", 0),
        }
        print(f"📤 PCStatusBroadcastConsumer: Broadcasting PC status update")
        print(f"   PC: {event.get('pc_name')}, Status: {event.get('booking_status')}")
        try:
            await self.send(text_data=json.dumps(message_data))
            print(f"✅ PC status update broadcast sent successfully")
        except Exception as e:
            print(f"❌ Error broadcasting PC status update: {e}")
            import traceback
            traceback.print_exc()
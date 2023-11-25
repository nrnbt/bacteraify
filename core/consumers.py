# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class TaskConsumer(AsyncWebsocketConsumer):
#   async def connect(self):
#     await self.channel_layer.group_add(
#       "survey_group",
#       self.channel_name
#     )
#     await self.accept()

#   async def disconnect(self, close_code):
#     await self.channel_layer.group_discard(
#       "survey_group",
#       self.channel_name
#     )

#   async def notify_survey_result(self, event):
#     data = event['data']
#     await self.send(json.dumps(data))
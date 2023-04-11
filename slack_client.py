# import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import SLACK_BOT_TOKEN

slack_client = WebClient(token=SLACK_BOT_TOKEN)

def get_message(channel_id: str, message_ts: str):
    try:
        response = slack_client.conversations_history(
            channel=channel_id,
            latest=message_ts,
            inclusive=True,
            limit=1
        )
        message = response["messages"][0]['text']
        return message
    except SlackApiError as e:
        print(f"Error getting message: {e}")
        return ''

# Send a message given a user, message text, and optional reactions
def send_message(user_id, message, extra_reactions = [], file_name = ''):
    try:
        if file_name != '':
            # Upload the file to Slack
            with open(file_name, "rb") as file:
                response = slack_client.files_upload(
                    channels=user_id,
                    file=file,
                    initial_comment=message
                )
        else:
            response = slack_client.chat_postMessage(
                channel=user_id,
                text=message
                )
        channelName = response['channel']
        message_ts = response['ts']
        
        reactions = [i for i in message.split(':') if ' ' not in i] + extra_reactions
        for reaction in reactions:
            slack_client.reactions_add(
                channel=channelName,
                timestamp=message_ts,
                name=reaction
            )
            
    except SlackApiError as e:
        print(f"Error sending {message} to user {user_id} with {extra_reactions}: {e}")
        return []

def get_users():
    try:
        response = slack_client.users_list()
        users = response["members"]
        return [user for user in users if not user["is_bot"]]
    except SlackApiError as e:
        print(f"Error getting users: {e}")
        return []
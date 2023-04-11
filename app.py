import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, reversed_messages, reaction_dic, specific_users
from slack_client import get_message, send_message
from user_management import invite_users, confirm_weekly_interest, ask_interests, save_users, load_users, confirm_weekly_interest_followup, get_user_profile
from pairings_manager import generate_pairings, save_pairings, read_pairings, swap_pairings, publish_and_send_dm

# Initialize Slack client and Bolt app
slack_client = WebClient(token=SLACK_BOT_TOKEN)
app = App(token=SLACK_BOT_TOKEN) #, client=slack_client)


@app.command("/lunchtag-invite")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)
    # specific_users = command["text"].split()
    respond("Sending invitations to specified users.")
    invite_users(specific_users)


@app.command("/lunchtag-confirm")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)
    respond("Clearing last weeks status and asking active members for weekly confirmation")
    confirm_weekly_interest()


@app.command("/lunchtag-confirm-followup")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    respond("Following up on asking members for weekly confirmation")
    confirm_weekly_interest_followup()


@app.command("/lunchtag-pairings")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)
    text = body['text']
    requester_id = body['user_id']

    file_name = read_pairings(text)
    send_message(requester_id, 'Here is pairing data that currently is saved', [], file_name)


@app.command("/lunchtag-generate")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)
    text = body['text']
    requester_id = body['user_id']

    respond("Generating pairings among Confirmed interested participants.")
    generated_df = generate_pairings(text)
    save_pairings(generated_df)
    file_name = read_pairings(text)
    send_message(requester_id, 'Here is pairing data that was just generated', [], file_name)


@app.command("/lunchtag-swap")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)
    text = body['text']
    requester_id = body['user_id']
    
    respond("Swapping pairings " + text[-5:])
    swapped_df = swap_pairings(text)
    save_pairings(swapped_df)
    file_name = read_pairings()
    send_message(requester_id, 'Here is swapped data that was just generated', [], file_name)


@app.command("/lunchtag-publish")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    respond("Publishing the final pairings and creating private chats.")
    publish_and_send_dm()
    respond('Just published!')


@app.command("/lunchtag-view-profile")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    requester_id = body['user_id']
    get_user_profile(requester_id)


@app.command("/lunchtag-interests")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    requester_id = body['user_id']
    user_data = load_users()
    if requester_id not in user_data:
        print('ignoring this message')
        return
    respond("Resetting your interests...")
    user_data[requester_id]['interests'] = []
    save_users(user_data)
    ask_interests(requester_id)


@app.command("/lunchtag-admin-status")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    requester_id = body['user_id']
    user_data = load_users()
    message = str(user_data)
    send_message(requester_id, message)

@app.command("/lunchtag-interests-custom")
def lunchtag_handler(ack, body, logger, respond):
    ack()
    logger.info(body)

    requester_id = body['user_id']
    user_data = load_users()
    if requester_id not in user_data:
        print('ignoring this reaction')
        return
    text = body['text']
    user_data[requester_id]['custom_interest'] = text
    save_users(user_data)
    respond("Set your new custom interest!")

# Reaction handling
@app.event("reaction_added")
def handle_reaction(body, logger):
    user_data = load_users()
    user_id = body['event']['user']
    reaction = body['event']['reaction']

    # get message text
    channel_id = body['event']['item']['channel']
    message_ts = body['event']['item']['ts']
    text = get_message(channel_id, message_ts)

    # get topic of Lunchbot message
    topic = reversed_messages.get(text, 'Fallback')

    # If we don't recognize this user or reaction for this topic, give up
    if reaction not in reaction_dic[topic].keys() or user_id not in user_data:
        print('ignoring this reaction')
        return

    if topic == 'invite':
        invitee_status = reaction_dic[topic][reaction]
        user_data[user_id]['status'] = invitee_status
        if invitee_status == 'joined':
            ask_interests(user_id)
        send_message(user_id, f'Your status has been updated to {invitee_status}')

    elif topic == 'weekly_interest':
        confirmation_status = reaction_dic[topic][reaction]
        user_data[user_id]["weekly_interest"] = confirmation_status
        send_message(user_id, f'Your interest this week has been updated to {confirmation_status}')


    elif topic == 'all_interests':
        interest = reaction_dic[topic][reaction]
        existing_interests = user_data[user_id]['interests']
        new_interests = list(set(existing_interests + [interest]))
        user_data[user_id]['interests'] = new_interests
        send_message(user_id, f'Your interests have been updated to {new_interests}')


    # Save updated user_data to the file
    save_users(user_data)


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)
    print(body)
    return


def main():
    # Set up the Socket Mode handler for receiving events
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
    
if __name__ == "__main__":
    main()
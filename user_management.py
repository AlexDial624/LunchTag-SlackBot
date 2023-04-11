import json
from slack_client import send_message, get_users
from config import messages

def load_users():
    """Load user data from the userdata.json file."""
    try:
        with open('userdata.json', 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}
    return user_data

def save_users(user_data):
    """Save updated user_data to the userdata.json file."""
    with open('userdata.json', 'w') as f:
        json.dump(user_data, f)


# invite all specific users
def invite_users(specific_users):
    """Invite specific users to join the event."""
    user_data = load_users()
    message = messages['invite']
    users = get_users()
    for user in users:
        user_id = user['id']
        real_name = user['real_name']

        if user_id in specific_users:
            if user_id not in user_data:
                user_data[user_id] = {'real_name': real_name,
                                        'status': 'noResponse',
                                       'weekly_interest': 'noResponse',
                                       'interests': [],
                                       'history': []
                                     }
            if user_data[user_id]['status'] == 'noResponse':
                print('Sending to ' + str(user_id))
                send_message(user_id, message)                
    save_users(user_data)

def confirm_weekly_interest():
    """Confirm weekly interest of users."""
    user_data = load_users()
    print('Confirming weekly interest')
    message = messages['weekly_interest']
    for user_id in user_data:
        if user_data[user_id]['weekly_interest'] != 'paused':
            user_data[user_id]['weekly_interest'] = 'noResponse'
        print(user_data[user_id]['weekly_interest'])
        if user_data[user_id]["status"] == "joined" and user_data[user_id]['weekly_interest'] == 'noResponse':
            send_message(user_id, message)
    save_users(user_data)

def confirm_weekly_interest_followup():
    """Confirm weekly interest of users."""
    user_data = load_users()
    print('Confirming weekly interest')
    message = messages['weekly_interest_followup']
    for user_id in user_data:
        if user_data[user_id]["status"] == "joined" and user_data[user_id]['weekly_interest'] == 'noResponse':
            send_message(user_id, message)
    save_users(user_data)

def ask_interests(user_id):
    """Ask the user about their interests."""
    message = messages['all_interests']
    print('asking interest of '+ user_id)
    send_message(user_id, message)

def update_user_history(user1_id, user1_name, user2_id, user2_name, meeting_date):
    """Update the history of user1 and user2 with the meeting details."""
    user_data = load_users()
    user_data[user1_id]['history'].append((meeting_date, user2_name))
    user_data[user2_id]['history'].append((meeting_date, user1_name))
    save_users(user_data)

def get_user_profile(requested_user_id):
    """Invite specific users to join the event."""
    user_data = load_users()
    message = messages['invite']
    if requested_user_id not in user_data.keys():
        message = messages['missing_user']
    else:
        requested_data = user_data[requested_user_id]
        message = messages['get_user_profile']
        message = message.format(**requested_data)
    send_message(requested_user_id, message)
    # Add functionality to change interests / edit profile


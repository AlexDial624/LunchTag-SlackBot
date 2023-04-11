import os

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# SLACK_BOT_TOKEN = "xoxb-3977975994593-5046380600870-f4DIjp4BJMZCoJciwoBla4Dk"
# SLACK_APP_TOKEN = 'xapp-1-A051XC4LK9P-5055648920244-10221e8449ffd3b90de1577f900a7215be012e444d3afd93ffca8e286d9fa5ab'

messages = {'invite': "Would you like to join the LunchTag program? React with :white_check_mark: for yes or :x: for no.",
            
            'weekly_interest': "Hey! For LunchTag this week, please react with a :white_check_mark: if you're ready for your next pairing,"
               " react a :mailbox: if you'd like to skip this week. You can also react :double_vertical_bar: if you like"
               " to pause your LunchTag subscription for a period",
            
            'weekly_interest_followup': 'Hey! We are sending out pairings soon, please respond to the last message to update your status!',
            
            'all_interests': 'What are you interested in talking about? :one: for AI, :two: for Animal Welfare, :three: for Community Building...',
            
            'missing_user': "Sorry, I couldn't find your profile in our database.",
            
            'get_user_profile': '{real_name}, here is your user profile:\n'
                '     • Status: {status}\n'
                '     • This Weeks Interest: {weekly_interest}\n'
                '     • Interests: {interests}\n'
                '     • LunchTag History: {history}'}


reversed_messages = dict(map(reversed, messages.items()))

specific_users = ["U03UFPNSDT6", "U03UD78Q7MZ"]




reaction_dic = {'invite': 
                    {"white_check_mark": 'joined', 
                    'x': 'declined'},
                'weekly_interest': 
                    {"white_check_mark": 'confirmed', 
                    'mailbox': 'skipping',
                    'double_vertical_bar': 'paused'},
                'all_interests': 
                    {'one': 'AI', 
                    'two': 'Animal Welfare',
                    'three': 'Community Building'},
                'Fallback': {}
                }

all_interests = {'one': 'AI', 'two': 'Animal Welfare', 'three': 'Community Building'}

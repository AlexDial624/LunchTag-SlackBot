import numpy as np
import pandas as pd
from tabulate import tabulate
from scipy.optimize import linear_sum_assignment
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import date

from slack_client import send_message
from user_management import save_users, load_users, update_user_history


def generate_pairings(text):
    user_data = load_users()
    users = [user_id for user_id, data in user_data.items() if data["weekly_interest"] == "confirmed"]
    num_users = len(users)
    compatibility_matrix = np.zeros((num_users, num_users))

    for i in range(num_users):
        for j in range(i + 1, num_users):
            user1 = users[i]
            user2 = users[j]

            common_interests = list(set(user_data[user1]['interests']) & set(user_data[user2]['interests']))
            score = len(common_interests) 

            if user2 in user_data[user1]['history'] and user1 in user_data[user2]['history']:
                score -= 10
            
            if user1 == user2:
                score -= 100

            compatibility_matrix[i, j] = score
            compatibility_matrix[j, i] = score

    row_ind, col_ind = linear_sum_assignment(-compatibility_matrix)

    final_pairings = []
    for i, j in zip(row_ind, col_ind):
        if i < j:
            user1 = users[i]
            user2 = users[j]
            common_interests = list(set(user_data[user1]['interests']) & set(user_data[user2]['interests']))
            score = compatibility_matrix[i, j]

            final_pairings.append({
                'Person 1': user_data[user1]['real_name'],
                'Person 2': user_data[user2]['real_name'],
                'Score': score,
                'Person 1 Interests': ', '.join(user_data[user1]['interests']),
                'Person 2 Interests': ', '.join(user_data[user2]['interests']),
                'Common Interests': ', '.join(common_interests),
                'Person 1 ID': user1,
                'Person 2 ID': user2
            })

    final_df = pd.DataFrame(final_pairings)
    return final_df


def swap_pairings(command):
    # Parse the command to get the corresponding row and column indices
    tokens = command[-5:].split()
    row1, cols1 = int(tokens[0][1]), [0,3,6] if tokens[0][0].upper() == 'A' else [1,4,7]
    row2, cols2 = int(tokens[1][1]), [0,3,6] if tokens[1][0].upper() == 'A' else [1,4,7]

    # Create a new DataFrame to store the updated pairingsmm
    df = read_pairings('full')
    new_df = df.copy()

    # Swap the users according to the specified row and column indices
    new_df.iloc[row1, cols1], new_df.iloc[row2, cols2] = new_df.iloc[row2, cols2], new_df.iloc[row1, cols1]

    for row in [row1, row2]:
        user1, user2 = new_df.iloc[row, -2], new_df.iloc[row, -1]
        common_interests = list(set(user_data[user1]['interests']) & set(user_data[user2]['interests']))
        score = len(common_interests) 
        if user2 in user_data[user1]['history'] and user1 in user_data[user2]['history']:
            score -= 10
        new_df.iloc[row, 2] = score
        new_df.iloc[row, 5] = ', '.join(common_interests)
        
    return new_df


def save_pairings(df):
    print('saving df...')
    df.to_excel("pairings_full.xlsx", index=False)
    return


def read_pairings(text='tiny'):
    final_df = pd.read_excel("pairings_full.xlsx")

    if 'short' in text:
        short_df = final_df.copy()[final_df.columns[0:5]]
        short_df_text = tabulate(short_df, tablefmt="grid", headers=short_df.columns)
        short_df = pd.DataFrame.from_dict([{'Summary': short_df_text}])
        short_df.to_csv("pairings_short.csv", index=False)
        return "pairings_short.csv"
    
    if 'full' in text:
        return "pairings_full.xlsx"
    
    tiny_df = final_df.copy()[final_df.columns[0:2]]
    tiny_df_text = tabulate(tiny_df, tablefmt="grid", headers=tiny_df.columns)
    tiny_df = pd.DataFrame.from_dict([{'Summary': tiny_df_text}])
    tiny_df.to_csv("pairings_tiny.csv", index=False)
    return "pairings_tiny.csv"


def publish_and_send_dm():
    user_data = load_users()
    file_name = read_pairings('full')
    final_df = pd.read_excel(file_name)
    meeting_date = date.today().strftime("%m/%d/%y")
    for index, row in final_df.iterrows():
        user1_id = row['Person 1 ID']
        user1_real_name = row['Person 1']
        user2_id = row['Person 2 ID']
        user2_real_name = row['Person 2']
        shared_interests = row['Common Interests']
        message_to_user1 = f"Hi {user1_real_name}, you've been paired up for LunchTag with <@{user2_id}>! You both share interests in {shared_interests}. Please initiate the conversation and plan a meetup. Enjoy!"
        message_to_user2 = f"Hi {user2_real_name}, you've been paired up for LunchTag with <@{user1_id}>! You both share interests in {shared_interests}. Please initiate the conversation and plan a meetup. Enjoy!"

        send_message(user1_id, message_to_user1)
        send_message(user2_id, message_to_user2)

        # Update user history
        update_user_history(user1_id, user_data[user1_id]['real_name'], user2_id, user_data[user2_id]['real_name'], meeting_date)
    print('Done sending dms!')
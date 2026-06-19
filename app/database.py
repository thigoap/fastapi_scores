from supabase import create_client

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
# for Supabase Google Oauth authentication
SUPA_GOOGLE_REDIRECT_URI_ENDPOINT = os.environ.get('SUPA_GOOGLE_REDIRECT_URI_ENDPOINT')
# for Supabase Google Oauth authentication

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def check_email(email):
    db_email = supabase.table('users').select('email').eq('email', email).execute().data
    return db_email


def check_username(username):
    db_user = supabase.table('users').select('username').eq('username', username).execute().data   
    return db_user


def get_counts():
    users_count = supabase.table('users').select('*', count= 'exact', head=False).execute().count
    guesses_count = supabase.table('guesses').select('*', count= 'exact', head=False).execute().count
    return [users_count, guesses_count]


def signup_user(email, username, invisible):   
    supabase.table('users').insert({
        'email': email,
        'username': username,
        'invisible': invisible
    }).execute()


def update_user(email, username, invisible):
    supabase.table('users').update({
        'username': username,
        'invisible': invisible
    }).eq('email', email).execute()


def update_user_guesses(email):
    guesses_num = supabase.table('guesses').select('*', count= 'exact', head=False).eq('user_email', email).execute().count
    supabase.table('users').update({
        'guesses': guesses_num
    }).eq('email', email).execute()


def delete_email(email):
    delete_user_guesses(email)
    supabase.table('users').delete().eq('email', email).execute()


def delete_user_guesses(email):
    supabase.table('guesses').delete().eq('user_email', email).execute().data


def get_profile_info(email):
    profile_info = supabase.table('users').select('*').eq('email', email).maybe_single().execute()
    return profile_info


def get_match_status():
    match_status = supabase.table('fixtures').select('match_id, status').execute().data

    matches_dict = {}
    for entry in match_status:
        m_id = entry['match_id']
        matches_dict [f"{m_id}"] = entry['status']
    return matches_dict


def record_guesses(email, guesses):
    match_status = get_match_status()

    # Create a container for grouped results
    grouped = {}

    for key, value in guesses.items():
        # Split the key (e.g., 'a01_home' becomes ['a01', 'home'])
        match_id, side = key.split('_')
    
        # Initialize the sub-dictionary if it doesn't exist, and if the match is still valid for guesses
        if match_id not in grouped and match_status[match_id] == 'enabled':
            grouped[match_id] = {'match_id': match_id}
    
        # Assign the score to the correct side
        if match_status[match_id] == 'enabled':
            grouped[match_id][side] = value

    # Convert the dictionary to a list of rows
    rows_to_insert = list(grouped.values())

    for guess in rows_to_insert:
        supabase.table('guesses').upsert({
            'guess_id': guess['match_id']+'_'+email,
            'user_email': email,
            'match_id': guess['match_id'],
            'guess_home': guess['home'],
            'guess_away': guess['away']
        }).execute()


def get_guesses(email):
    guesses = supabase.table('guesses').select('match_id, guess_home, guess_away, points_earned').eq('user_email', email).execute().data

    guesses_dict = {}

    for entry in guesses:
        m_id = entry['match_id']
        guesses_dict [f"{m_id}_home"] = entry['guess_home']
        guesses_dict [f"{m_id}_away"] = entry['guess_away']
        guesses_dict [f"{m_id}_points"] = entry['points_earned']
    #print(guesses_dict)
    return guesses_dict


def get_fixtures_results():
    results = supabase.table('fixtures').select('match_id, home_team_score, away_team_score').execute().data

    results_dict = {}

    for entry in results:
        m_id = entry['match_id']
        results_dict [f"{m_id}_home"] = entry['home_team_score']
        results_dict [f"{m_id}_away"] = entry['away_team_score']
    #print(results_dict)

    filtered_results_dict = {k: v for k, v in results_dict.items() if v is not None}
    print(filtered_results_dict)

    return filtered_results_dict


def get_rank():
    rank = supabase.table('users').select('*').execute().data
    return rank


def get_visible_rank():
    visible_rank = supabase.table('users').select('username, points, guesses').order('points', desc=True).eq('invisible', False).execute().data
    #print(visible_rank)

    # Ranked Leaderboard
    """     ranked_leaderboard = [
       {**user, 'position': i} 
        for i, user in enumerate(visible_rank, 1)
    ]
    print('Ranked leaderboard -------------------------------')
    print(ranked_leaderboard) """
 
    # Ranked Leaderboard considering draws
    ranked_leaderboard = []
    current_rank = 0
    last_points = None

    for i, user in enumerate(visible_rank, 1):
        # Only increase the rank if the points are different from the previous user
        if user['points'] != last_points:
            current_rank = i
        
        ranked_leaderboard.append({**user, 'position': current_rank})
        last_points = user['points']

    print('Ranked Leaderboard considering draws -------------------------------')
    print(ranked_leaderboard)

    return ranked_leaderboard

""" def get_matches_info():
    matches_info = []
    matches = supabase.table('fixtures').select('*, national_teams(name_pt, flag_image_url)').execute().data
    for match in matches:
        home_team_id = match['home_team_id']
        away_team_id = match['away_team_id']
        match_date = match['date']
        home_team_info = supabase.table('national_teams').select('name_pt, flag_image_url').eq('team_id', home_team_id).execute().data
        away_team_info = supabase.table('national_teams').select('name_pt, flag_image_url').eq('team_id', away_team_id).execute().data
        match_dict = {
            'match_date': match_date,
            'home_team_name': home_team_info[0]['name_pt'],
            'home_team_flag': home_team_info[0]['flag_image_url'],
            'away_team_name': away_team_info[0]['name_pt'],
            'away_team_flag': away_team_info[0]['flag_image_url']
        }
        matches_info.append(match_dict)
    return matches_info """

import requests

SUPABASE_URL = 'https://your-project.supabase.co'
SUPABASE_API_KEY = 'your-anon-key'

def get_users():
    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}'
    }
    response = requests.get(f'{SUPABASE_URL}/rest/v1/users', headers=headers)
    return response.json()

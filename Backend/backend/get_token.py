import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)
res = supabase.auth.sign_in_with_password({'email': 'mukunthgopi@gmail.com', 'password': 'Lggm2006$'})
print(res.session.access_token)

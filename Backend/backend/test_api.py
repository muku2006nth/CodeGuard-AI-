import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)
res = supabase.auth.sign_in_with_password({'email': 'mukunthgopi@gmail.com', 'password': 'Lggm2006$'})
token = res.session.access_token

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
body = {"code": "import os\n\ndef run_cmd(user_input):\n    # Vulnerable: command injection\n    os.system(user_input)\n\npassword = 'hardcoded_secret'", "language": "python"}
try:
    response = requests.post("http://localhost:5173/api/analyze", headers=headers, json=body)
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
except Exception as e:
    print("Exception:", e)

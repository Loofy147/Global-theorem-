import os
import requests
import base64
import json

token = "github_pat_11BKWH6MI0mIzqUWKHyxEX_KO92xoWx25JHq96tT4DK64FlhWr3gOO57S0XBmeg8bNS662LXRE85uyIE5"
url = "https://api.github.com/repos/hichambedrani/Global-theorem-/contents/fso_manifold_state.json"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

res = requests.get(url, headers=headers)
if res.status_code == 200:
    content = json.loads(base64.b64decode(res.json()['content']).decode())
    print(f"Remote Timestamp: {content.get('timestamp')}")
    print(f"Remote Health Check: {content.get('registry', {}).get('system.last_check')}")
else:
    print(f"Error fetching remote state: {res.status_code}")

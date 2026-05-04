import requests

TOKEN = "8726779674:AAGzRxWTQ21fE_iHNwSy5t_rbqQBdkOdiL0"

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url)

print(response.json())
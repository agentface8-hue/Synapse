import requests
r = requests.get('https://agentface8.com', timeout=60)
print(len(r.text), 'bytes')
# Check if bundled JS references LandingPage
print('LandingPage in html:', 'LandingPage' in r.text or 'landing' in r.text.lower())
print('_next in html:', '_next' in r.text)

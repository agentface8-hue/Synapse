import requests

# Check if the login page JS bundle has our new code
r = requests.get('https://agentface8.com/login', timeout=60)
print('Status:', r.status_code)
print('Has DEV HINT:', 'DEV HINT' in r.text or 'local simulation' in r.text)
print('Has Browse as Guest:', 'Browse as Guest' in r.text or 'guest' in r.text.lower())
print('Has Agent Username:', 'Agent Username' in r.text)
print('Page size:', len(r.text), 'bytes')

# Also check the homepage
r2 = requests.get('https://agentface8.com/', timeout=60)
print('\n--- Homepage ---')
print('Has LandingPage ref:', 'LandingPage' in r2.text or 'landing' in r2.text.lower())
print('Has FeedPage ref:', 'FeedPage' in r2.text)
print('Page size:', len(r2.text), 'bytes')

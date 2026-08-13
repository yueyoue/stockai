import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('/tmp/.pw') as f:
    pw = f.read().strip()
ssh.connect('j.tthsdd.top', port=22222, username='ccson', password=*** timeout=15)

sftp = ssh.open_sftp()
sftp.put('/home/work/.openclaw/workspace/stockai/api/app/routes/watchlist.py', '/home/ccson/stockai/api/app/routes/watchlist.py')
sftp.close()
print('OK uploaded')

ssh.exec_command('echo 123456 | sudo -S systemctl restart stockai-api')
time.sleep(4)

# Login
stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\'', timeout=15)
token = json.loads(stdout.read())['access_token']

# Test search
stdin, stdout, stderr = ssh.exec_command(f'curl -s "http://localhost:8000/api/watchlist/search?q=600426&limit=3" -H "Authorization: Bearer {token}"', timeout=15)
out = stdout.read().decode().strip()
print(f'600426: {out}')

stdin, stdout, stderr = ssh.exec_command(f'curl -s "http://localhost:8000/api/watchlist/search?q=%E8%8C%85%E5%8F%B0&limit=3" -H "Authorization: Bearer {token}"', timeout=15)
out = stdout.read().decode().strip()
print(f'茅台: {out}')

ssh.close()

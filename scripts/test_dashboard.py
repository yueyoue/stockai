import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('j.tthsdd.top', port=22222, username='ccson', password=*** timeout=15)

# Login
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST http://localhost:8000/api/auth/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin123"}\'',
    timeout=15
)
data = json.loads(stdout.read().decode().strip())
token = data['access_token']

# Test market
print("=== 大盘数据 ===")
stdin, stdout, stderr = ssh.exec_command(
    f'curl -s --max-time 30 http://localhost:8000/api/dashboard/market '
    f'-H "Authorization: Bearer {token}"',
    timeout=35
)
out = stdout.read().decode().strip()
print(out[:800])

# Test watchlist
print("\n=== 自选股看板 ===")
stdin, stdout, stderr = ssh.exec_command(
    f'curl -s --max-time 60 http://localhost:8000/api/dashboard/watchlist '
    f'-H "Authorization: Bearer {token}"',
    timeout=65
)
out = stdout.read().decode().strip()
print(out[:800])

# Check API logs
print("\n=== API 日志 ===")
stdin, stdout, stderr = ssh.exec_command('tail -15 /home/ccson/stockai/api.log 2>&1', timeout=10)
print(stdout.read().decode().strip())

ssh.close()

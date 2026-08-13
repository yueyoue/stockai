import paramiko, json, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
pw = os.environ.get('SSHPASS', '')
if not pw:
    with open('/tmp/.pw') as f:
        pw = f.read().strip()
ssh.connect('j.tthsdd.top', port=22222, username='ccson', password=*** timeout=15)

# Check admin
stdin, stdout, stderr = ssh.exec_command('docker exec stock-pg psql -U stock -d stockai -c "SELECT user_id, username, substring(password_hash,1,30) FROM users;"', timeout=10)
print('DB:', stdout.read().decode().strip())

# Login
stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"***"}\'', timeout=15)
print('Login:', stdout.read().decode().strip()[:200])

# Check frontend
stdin, stdout, stderr = ssh.exec_command('ls /var/www/stockai/assets/ | grep -i stock', timeout=10)
print('Stock:', stdout.read().decode().strip())

ssh.close()

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('j.tthsdd.top', port=22222, username='ccson', password=*** timeout=15)

sftp = ssh.open_sftp()
sftp.put('/home/work/.openclaw/workspace/stockai/scripts/test_dashboard.py', '/home/ccson/stockai/scripts/test_dashboard.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command('~/stockai/venv/bin/python3 ~/stockai/scripts/test_dashboard.py 2>&1', timeout=120)
print(stdout.read().decode().strip())

ssh.close()

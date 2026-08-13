from passlib.context import CryptContext
import subprocess

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_hash = pwd_context.hash("admin123")
print("Hash:", new_hash)

# Update via psql - need to escape the hash properly
cmd = f'docker exec stock-pg psql -U stock -d stockai -c "UPDATE users SET password_hash = \'{new_hash}\' WHERE username = \'admin\';"'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Result:", result.stdout.strip())
if result.stderr:
    print("Error:", result.stderr.strip()[:200])

from jose import jwt

# Token from login
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc4NjcxMzY3NH0.amqd6bNNOC7rRmv1tHdTum1VaFRCmSCUKr3Y1hgcgNM"
secret = "stockai-secret-key-2024-change-me"

try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    print("Decoded:", payload)
except Exception as e:
    print("Error:", e)

# Try without verification to see contents
payload = jwt.get_unverified_claims(token)
print("Unverified:", payload)

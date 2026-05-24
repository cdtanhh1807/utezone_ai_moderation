from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "hcmute@mypass"

hashed = pwd_context.hash(password)
print(hashed)

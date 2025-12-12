# app/core/limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the Limiter
# key_func=get_remote_address means we identify users by their IP address
limiter = Limiter(key_func=get_remote_address)
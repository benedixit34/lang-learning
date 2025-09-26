import random
import string


def generate_referral_code(length=15):
    # Generate a random string of uppercase letters
    letters = string.ascii_uppercase
    return "".join(random.choice(letters) for _ in range(length))

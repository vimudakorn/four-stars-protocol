import random
import string


def generate_unique_room_number(existing_numbers):
    while True:
        room_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if room_number not in existing_numbers:
            return room_number

# Example usage
existing_numbers = set()  # A set to keep track of existing room numbers
for i in range(5):
    new_room_number = generate_unique_room_number(existing_numbers)
    existing_numbers.add(new_room_number)

# print("New unique room number:", new_room_number)
print(existing_numbers)
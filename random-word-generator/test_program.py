import time
import os
# uuid basically makes sure that each request will have unique process id
# you can read about it here:
# https://docs.python.org/3/library/uuid.html
import uuid


def make_request(request):
    with open('request.txt', 'w') as file:
        file.write(request)
    print(f"request.txt: {request}")


def read_response():
    while not os.path.exists('response.txt') or os.path.getsize('response.txt') == 0:
        # wait for response
        time.sleep(0.1)
    with open('response.txt', 'r') as file:
        response = file.read().strip()
    print(f"response.txt: {response}")
    return response


if __name__ == "__main__":
    # clearing response.txt before making a request, making space for new word
    open('response.txt', 'w').close()
    # make a request with a unique identifier
    request_id = str(uuid.uuid4())

    make_request(f"RANDOM_WORD_{request_id}")
    # Read the response
    random_word = read_response()
    print("Generated word:", random_word)
    if len(random_word) == 5:
        print("Length OK :)")
    else:
        print("Length not valid! :(")
    # wipe response.txt for the next iteration
    open('response.txt', 'w').close()
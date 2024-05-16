import time
import os


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
    # Basic tests
    make_request("RANDOM_WORD")
    random_word = read_response()
    print("Generated word:", random_word)
    if len(random_word) == 5:
        print("Length OK :)")
    else:
        print("Length not valid! :(")
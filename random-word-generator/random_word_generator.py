import time
import requests

# connect to api
RANDOM_WORD_API_URL = "https://random-word-api.herokuapp.com/word?length=5"

# this will help with the request.txt having the stuff in it
last_processed_request = None


def get_word():
    response = requests.get(RANDOM_WORD_API_URL)
    # if successful
    if response.status_code == 200:
        # grab the first word from the response
        generated_word = response.json()[0]
        print(f"Generated word: {generated_word}")
        return generated_word
    return "ERROR getting the word! :("


def read_request():
    try:
        with open('request.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def write_response(response):
    with open('response.txt', 'w') as file:
        file.write(response)


def handle_request(request):
    if request.startswith("RANDOM_WORD"):
        response = get_word()
    else:
        response = "Failed request"
    return response


def main():
    global last_processed_request
    while True:
        request = read_request()
        if request and request != last_processed_request:
            response = handle_request(request)
            write_response(response)
            # update the last processed request
            last_processed_request = request
            # with the unique id
            print(f"Processed request: {request}")
            # wipe the request file after processing
            open('request.txt', 'w').close()
        time.sleep(1)


if __name__ == "__main__":
    main()


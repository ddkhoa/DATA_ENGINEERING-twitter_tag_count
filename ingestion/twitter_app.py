import socket
import string
import sys
import requests
import json
import argparse

parser = argparse.ArgumentParser(description='Pull tweets data stream, wait for connection then send data to processing layer')
parser.add_argument("--twitter_bearer_token", type=str, required=True, help="Tweeter API bearer token")
args = parser.parse_args()

BEARER_TOKEN = args.twitter_bearer_token

def bearer_oauth(r):
    
    r.headers["Authorization"] = "Bearer {}".format(BEARER_TOKEN)
    r.headers["User-Agent"] = "v2FilteredStreamPython"

    return r

def get_tweets():
    url = "https://api.twitter.com/2/tweets/search/stream"
    response = requests.get(url, auth=bearer_oauth, stream=True)

    return response

def send_tweets_to_spark(stream, tcp_connection):

    for response_line in stream.iter_lines():
        try : 
            json_response = json.loads(response_line)
            tweet_text = json_response['data']['text']
            print("Tweet text: " + tweet_text)
            print ("------------------------------------------")
            tcp_connection.send((tweet_text + '\n').encode())
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)

# Run the TCP server, wait for connections
# If there is, start sending tweets

TCP_IP="localhost"
TCP_PORT=9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection ... ")

conn, addr = s.accept()
print("Connected ... Starting getting tweets.")

stream = get_tweets()
send_tweets_to_spark(stream, conn)

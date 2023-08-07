import random
import socket
import sys
import praw

# Set your Reddit app credentials here
CLIENT_ID = "YOUR_CLient_ID"
CLIENT_SECRET = "YourClientSecret"
SCOPES = ["identity", "read"]  # Add the required scopes as a list

def receive_connection():
    """Wait for and then return a connected socket.

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


def main():
    """Provide the program's entry point when directly executed."""
    reddit = praw.Reddit(
        client_id=CLIENT_ID.strip(),
        client_secret=CLIENT_SECRET.strip(),
        redirect_uri="http://localhost:8080",
        user_agent="YourUserAgent",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(SCOPES, state, "permanent")
    print(f"Now open this URL in your browser: {url}")
    sys.stdout.flush()

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    refresh_token = reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

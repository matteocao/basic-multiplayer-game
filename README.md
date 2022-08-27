# Basic multiplayer game in python

This repo contains the code for a very basic multiplayer game built with `pygame`.

This game only supports 2 clients (the two players) and the interface only starts if there are two players connected.

The commands:
 - move with ASDW
 - shoot with E
 
## Basic logic
 
The server will listen for new clients -- that must connect t the server via socket.
 
Then, each client will constantly send information to the server about its intentions and the server will continuously update the game status (players' position, health, ...).

## How to play

Make sure you first run the server with

```
python server.py
```

and then connect with at least two clients:

```
python main.py
```

Ideally, you would deploy the server (and run the command `python server.py` from a place that two clients, on two different computers, can reach.

## Testing

TBA
#online multiplayer testing

import asyncio
import websockets
import pickle


async def sendUpdate(app):
    data = {"stateDict": app.stateDict,
    "playerName": app.playerName,
    "selectedParty": app.selectedParty,
    "selectedIssues": app.selectedIssues,
    "player1": app.player1,
    "player2": app.player2,
    "turns": app.turns,
    "rounds": app.rounds,
    "gameOver": app.gameOver,
    "winner": app.winner,
    "move": app.move,
    "currentIssue": app.currentIssue,
    "currentState": app.currentState,
    "currentPlayer": app.currentPlayer
    }

    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # pickledData = pickle.dumps(data)

        await websocket.send('pickledData')
        print(f"data sent")


async def listener():
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websocket:
        pickledData = await websocket.recv()
        data = pickle.loads(pickledData)
        print(data["move"])
        asyncio.get_event_loop().close()
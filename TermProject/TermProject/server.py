#online multiplayer testing

import asyncio
import websockets
import pickle


async def middleMan(websocket, path):
    pickledData = await websocket.recv()
    print(f"got the data")

    await websocket.send(pickledData)
    print(f"sent back new data")

start_server = websockets.serve(middleMan, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

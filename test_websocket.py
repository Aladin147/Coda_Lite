import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")
        
        # Send stt_start message
        start_message = {
            "type": "stt_start",
            "data": {
                "mode": "push_to_talk",
                "duration": 5
            }
        }
        await websocket.send(json.dumps(start_message))
        print("Sent stt_start message")
        
        # Wait for 2 seconds
        await asyncio.sleep(2)
        
        # Send stt_stop message
        stop_message = {
            "type": "stt_stop",
            "data": {}
        }
        await websocket.send(json.dumps(stop_message))
        print("Sent stt_stop message")
        
        # Wait for 5 seconds to receive any responses
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

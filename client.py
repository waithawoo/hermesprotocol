import asyncio
import socket
from protocol import HermesProtocol

class HermesClient:
    def __init__(self, host: str, port: int, encryption_key: bytes = b'\x01'):
        self.host = host
        self.port = port
        self.protocol = HermesProtocol(encryption_key)
        self.USE_SOCKET_LIB = True # I think socket lib is faster (not sure)
        
    async def send_request(self, message_type: int, payload: bytes):
        """Send a message to the server."""
        try:
            message = self.protocol.create_message(message_type, payload)
            print('Created message before send ', message)

            if self.USE_SOCKET_LIB:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    s.sendall(message)
                    print(f"Sent: {message}")
                    
                    response = s.recv(1024)
                    print(f"Received: {response}")
                    s.close()
                    return response
            else:
                try:
                    reader, writer = await asyncio.open_connection(self.host, self.port)
                    writer.write(message)
                    await writer.drain()
                    print(f"Sent: {message}")
                    
                    response = await reader.read(1024)
                    print(f"Received: {response}")
                    
                    return response
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    if writer:
                        writer.close()
                        await writer.wait_closed()
        except Exception as e:
            print(f"Error: {e}")

    async def run(self, message_type: int, payload: bytes):
        """Run the client to send a message."""
        response = await self.send_request(message_type, payload)
        response_type, response_payload = self.protocol.parse_message(response)
        print(f"Parased Response -> Received: {response_type}, Payload: {response_payload.decode()}")

async def main():
    host = '127.0.0.1'
    port = 65432
    
    runConcurrently = False
    trials = 10000
    
    if runConcurrently:
        clients = []
        for i in range(trials):
            message = f"Hello from Client {str(i)}".encode()
            client = HermesClient(host, port)
            clients.append(client.run(1, message))
        # Run all clients concurrently
        await asyncio.gather(*clients)
    else:
        for i in range(trials):
            message = f"Hello from Client {str(i)}".encode()
            client = HermesClient(host, port)
            await client.run(1, message)

if __name__ == '__main__':
    asyncio.run(main())


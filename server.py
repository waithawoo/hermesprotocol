import asyncio
from protocol import HermesProtocol

class HermesServer:
    def __init__(self, host: str, port: int, encryption_key: bytes = b'\x01'):
        self.host = host
        self.port = port
        self.protocol = HermesProtocol(encryption_key)

    async def handle_client(self, reader, writer):
        """Handle incoming client connections."""
        try:
            data = await reader.read(1024)
            
            print(f"Request data: {data}")
            if not data:
                print("Received empty data, closing connection.")
                return
            
            message_type, payload = self.protocol.parse_message(data)
            print(f"Parsed Requestdata => Received: {message_type}, Payload: {payload.decode()}")
            
            response_payload = b"Message processed successfully by " + payload
            response = self.protocol.create_message(2, response_payload)
                        
            writer.write(response)
            await writer.drain()
            print(f"Sent: {response}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        """Run the server to listen for connections."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        # print('server.sockets ', server.sockets)
        # print('server.sockets ', server.sockets[0])
        addr = server.sockets[0].getsockname()
        print(f'Server is running on {addr}')
        
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = HermesServer('127.0.0.1', 65432)
    asyncio.run(server.run())

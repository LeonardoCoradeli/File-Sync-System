# server/server_main.py
import http.server
import socketserver
import logging
from server.dispatcher import RMIDispatcherHandler

# 5. Threads no Servidor: Using ThreadingMixIn for concurrent request handling
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server(port=8000):
    server_address = ('', port)
    # Use the threaded server and our custom handler
    httpd = ThreadedHTTPServer(server_address, RMIDispatcherHandler)
    logging.info(f"Starting RMI simulation server on port {port}...")
    print(f"Server running on port {port}. Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        logging.info("Server stopped by user.")
    finally:
        httpd.server_close() # Clean up the server socket


if __name__ == "__main__":
    # Ensure log configuration is done early (e.g., in dispatcher or here)
    log_file = "server/sync.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    run_server()
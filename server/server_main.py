import http.server
import socketserver
import logging
from server.dispatcher import RMIDispatcherHandler

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def run_server(port=8000):
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, RMIDispatcherHandler)
    logging.info(f"Starting RMI simulation server on port {port}...")
    print(f"Server running on port {port}. Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        logging.info("Server stopped by user.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
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
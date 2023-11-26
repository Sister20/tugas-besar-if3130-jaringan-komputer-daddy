import argparse

class Parser:
    def __init__(self, server: bool):
        self.parser = self.create_server_parser() if server else self.create_client_parser()
        self.args = self.parser.parse_args()

    def create_server_parser():
        parser = argparse.ArgumentParser(description="Server Script")
        parser.add_argument("broadcast_port", type=int, help="Broadcast port for server")
        parser.add_argument("input_file", type=str, help="Path to the input file")
        return parser

    def create_client_parser():
        parser = argparse.ArgumentParser(description="Client Script")
        parser.add_argument("client_port", type=int, help="Client port")
        parser.add_argument("broadcast_port", type=int, help="Broadcast port for server")
        parser.add_argument("output_file", type=str, help="Path to the output file")
        return parser
    
    def get_args(self):
        if self.server:
            return {
                "broadcast_port": self.args.broadcast_port,
                "input_file": self.args.input_file
            }
        else:
            return {
                "client_port": self.args.client_port,
                "broadcast_port": self.args.broadcast_port,
                "output_file": self.args.output_file
            }
    
    def __str__(self):
        if self.server:
            return f"[Server Arguments]\nBroadcast Port: {self.args.broadcast_port}\nInput File: {self.args.input_file}"
        else:
            return f"[Client Arguments]\nClient Port: {self.args.client_port}\nBroadcast Port: {self.args.broadcast_port}\nOutput File: {self.args.output_file}"

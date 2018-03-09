class Controller:
    def __init__(self, server_name):
        self.arg = arg

        # Create bluetooth server and start it listening on a new thread
        server = ev3_server.BluetoothServer(server_name, self.parse_message)
        server_thread = Thread(target=server.start_server)
        server_thread.start()

    def parse_message(data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'move' and len(command_args) == 3 and
                'ports' in command_args.keys() and 'speed' in command_args.keys() and 'time' in command_args.keys()):
                rotate_motor(command_args['ports'], command_args['speed'], command_args['time'])

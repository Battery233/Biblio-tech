import control

class AuxController(control.Controller):
    def __init__(self, server_name):
        super().__init__(server_name)



if __name__ == '__main__':
    # Initialize auxiliary brick, starts listening for commands
    brick = MainController('ev3_aux')

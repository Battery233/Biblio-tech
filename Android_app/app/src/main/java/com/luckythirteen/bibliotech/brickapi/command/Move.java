package com.luckythirteen.bibliotech.brickapi.command;

import com.luckythirteen.bibliotech.brickapi.obj.OutputPort;

/**
 * Move specified motors at a certain speed for a defined amount of time
 */

public class Move extends Command {

    private int speed;
    private int time;
    private OutputPort[] ports;

    /**
     * @param speed Motor speed (deg / sec)
     * @param time  Motor run time (ms)
     * @param ports Output ports to send command to
     */
    public Move(int speed, int time, OutputPort[] ports) {
        this.speed = speed;
        this.time = time;
        this.ports = ports;
        this.commandType = CommandType.move;
    }
}

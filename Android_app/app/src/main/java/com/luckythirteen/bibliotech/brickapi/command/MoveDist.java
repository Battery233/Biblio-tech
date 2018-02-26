package com.luckythirteen.bibliotech.brickapi.command;

import com.luckythirteen.bibliotech.brickapi.obj.OutputPort;

/**
 * Created by s1546623 on 25/02/18.
 */

public class MoveDist extends Command {
    private OutputPort port;
    private float dist;
    private int speed;

    /**
     * Moves motor by a specified distance (cm) and speed (degrees/cm)
     *
     * @param port  Port to send command to
     * @param dist  Distance to move motor in centimetres
     * @param speed Speed to move motor (degrees/cm)
     */
    public MoveDist(OutputPort port, float dist, int speed) {
        this.port = port;
        this.dist = dist;
        this.speed = speed;
        this.commandType = CommandType.moveDist;
    }
}

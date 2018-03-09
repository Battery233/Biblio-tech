package com.luckythirteen.bibliotech.brickapi.command;

import com.luckythirteen.bibliotech.brickapi.obj.OutputPort;

/**
 * Created by s1546623 on 25/02/18.
 */

public class MoveDist extends Command {
    private OutputPort[] ports;
    private float dist;
    private int speed;

    /**
     * Moves motor by a specified distance (cm) and speed (degrees/cm)
     *
     * @param ports  Ports to send command to
     * @param dist  Distance to move motor in centimetres
     * @param speed Speed to move motor (degrees/cm)
     */
    public MoveDist(OutputPort[] ports, float dist, int speed) {
        this.ports = ports;
        this.dist = dist;
        this.speed = speed;
        this.commandType = CommandType.moveDist;
    }
}

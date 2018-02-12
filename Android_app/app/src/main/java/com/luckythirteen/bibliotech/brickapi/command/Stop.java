package com.luckythirteen.bibliotech.brickapi.command;

import com.luckythirteen.bibliotech.brickapi.obj.OutputPort;

/**
 * Stop motors
 */

public class Stop extends Command
{
    private OutputPort[] ports;

    /**
     * @param ports Output ports to send command to
     */
    public Stop(OutputPort[] ports)
    {
        this.ports = ports;
        this.commandType = CommandType.stop;
    }
}

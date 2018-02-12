package com.luckythirteen.bibliotech.brickapi.obj;

/**
 * Represents the input ports on the EV3 brick
 */

public enum InputPort
{
    ONE, // in1
    TWO,  // in2
    THREE, // in
    FOUR;

    @Override
    public String toString()
    {
        return "in" + Integer.toString(this.ordinal() + 1);
    }
}

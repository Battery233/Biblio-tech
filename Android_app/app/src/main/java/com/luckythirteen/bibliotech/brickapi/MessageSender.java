package com.luckythirteen.bibliotech.brickapi;


import android.util.Log;

import com.luckythirteen.bibliotech.brickapi.command.Command;

import co.lujun.lmbluetoothsdk.BluetoothController;
import co.lujun.lmbluetoothsdk.base.State;

/**
 * Send messages to brick
 */

public class MessageSender {
    private static final String TAG = "MessageSender";
    private final BluetoothController bluetoothController;

    public MessageSender(BluetoothController bluetoothController) {
        this.bluetoothController = bluetoothController;
    }

    /**
     * Sends a command to the brick
     *
     * @param c Command to send
     * @return True if succeeded, false otherwise
     */
    public boolean sendCommand(Command c) {
        return sendMessage(c.toJSONString());
    }

    /**
     * Sends a string to the brick
     *
     * @param s String to send
     * @return True if succeeded, false otherwise
     */
    public boolean sendMessage(String s) {
        try {
            if (bluetoothController.getConnectionState() == State.STATE_CONNECTED) {
                bluetoothController.write(s.getBytes());
                return true;
            } else {
                return false;
            }
        } catch (Exception e) {
            Log.e(TAG, e.getMessage());
            return false;
        }
    }
}

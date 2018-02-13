package com.luckythirteen.bibliotech.brickapi;


import android.util.Log;

import com.luckythirteen.bibliotech.brickapi.command.Command;

import co.lujun.lmbluetoothsdk.BluetoothController;

/**
 * Send messages to brick
 */

public class MessageSender {
    private static final String TAG = "MessageSender";
    private BluetoothController bluetoothController;

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
    private boolean sendMessage(String s) {
        try {
            bluetoothController.write(s.getBytes());
            return true;
        } catch (Exception e) {
            Log.e(TAG, e.getMessage());
            return false;
        }
    }
}

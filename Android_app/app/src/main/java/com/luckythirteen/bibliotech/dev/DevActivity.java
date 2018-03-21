package com.luckythirteen.bibliotech.dev;

/* The bluetooth java class
 */

import android.bluetooth.BluetoothDevice;
import android.graphics.drawable.ShapeDrawable;
import android.graphics.drawable.shapes.OvalShape;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.MessageSender;
import com.luckythirteen.bibliotech.brickapi.command.Move;
import com.luckythirteen.bibliotech.brickapi.command.MoveDist;
import com.luckythirteen.bibliotech.brickapi.command.Stop;
import com.luckythirteen.bibliotech.brickapi.obj.OutputPort;
import com.luckythirteen.bibliotech.storage.UserPrefsManager;

import java.util.ArrayList;
import java.util.UUID;

import co.lujun.lmbluetoothsdk.BluetoothController;
import co.lujun.lmbluetoothsdk.base.BluetoothListener;
import co.lujun.lmbluetoothsdk.base.State;


public class DevActivity extends AppCompatActivity {

    private static final String TAG = "DevActivity";

    // MAC addresses
    // private static final String TARGET_MAC = "AC:FD:CE:2B:82:F1";                                   // Colin's laptop
    // private static final String TARGET_MAC = "78:0c:b8:0b:a0:44";                                   // Chenghao's laptop
    private static String TARGET_MAC = "B0:B4:48:76:E7:86";                                      // EV3 33

    // UI elements
    private TextView bluetoothStatus;
    private TextView spinDurationLabel;
    private EditText messageText, speedText, durationText;
    private ImageButton reconnectButton;
    private SeekBar durationBar;
    private CheckBox distanceModeCheckBox;
    private CheckBox boxA, boxB, boxC, boxD;

    // BluetoothController object for creating a connection to the EV3
    private static BluetoothController bluetoothController;

    // UUID of bluetooth connection (must be set the same on the EV3 bluetooth server)
    public static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    // Max speed and max duration to allow app to send to robot (for motors)
    private static final int MAX_SPEED = 999; // degrees per second
    private static final int MAX_DURATION = 9999; // milliseconds
    private static final int MAX_DISTANCE = 600; // millimetres

    private MessageSender messageSender;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d(TAG, "onCreate()");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dev);

        setupUI();

        // Use stored mac address
        TARGET_MAC = new UserPrefsManager(this.getApplicationContext()).getMacAddress();

        // For classic bluetooth
        bluetoothController = BluetoothController.getInstance().build(this);
        bluetoothController.setAppUuid(MY_UUID);

        bluetoothController.setBluetoothListener(bluetoothListener);
        bluetoothController.connect(TARGET_MAC);

        messageSender = new MessageSender(bluetoothController);
    }

    private final BluetoothListener bluetoothListener = new BluetoothListener() {
        @Override
        public void onReadData(BluetoothDevice device, byte[] data) {
            final String msg = new String(data);
            Log.d(TAG, "Received: " + msg);

            // Make a toast appear with the message received from the EV3 brick (have to run on UI thread otherwise an error is thrown)
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        //see if the message send back is the location string
                        float location = Float.valueOf(msg) * (float) 1;
                        if (location < 60000 && location > -60000) {
                            if (location < 0.01 && location > -0.01) {
                                location = (float) 0.0;
                            }
                            Toast.makeText(DevActivity.super.getApplicationContext(), "current location:" + location, Toast.LENGTH_SHORT).show();
                            System.out.print(">>>" + TAG + "get location feedback");
                        } else {
                            Toast.makeText(DevActivity.super.getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
                        }
                    } catch (Exception e) {
                        Toast.makeText(DevActivity.super.getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
                    }
                }
            });

            // Vibrate phone (different methods depending on API version)
            if (Build.VERSION.SDK_INT >= 26) {
                try {
                    ((Vibrator) getSystemService(VIBRATOR_SERVICE)).vibrate(VibrationEffect.createOneShot(150, VibrationEffect.DEFAULT_AMPLITUDE));
                } catch (Exception ignored) {
                }
            } else {
                try {
                    ((Vibrator) getSystemService(VIBRATOR_SERVICE)).vibrate(150);
                } catch (Exception ignored) {
                }
            }

        }

        @Override
        public void onActionStateChanged(int preState, int state) {

        }

        @Override
        public void onActionDiscoveryStateChanged(String discoveryState) {

        }

        @Override
        public void onActionScanModeChanged(int preScanMode, int scanMode) {

        }

        @Override
        public void onBluetoothServiceStateChanged(int state) {
            Log.d(TAG, "BT STATE: " + state);
            updateBluetoothStatusUI(state);
        }

        @Override
        public void onActionDeviceFound(BluetoothDevice device, short rssi) {

        }
    };

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume()");
        updateBluetoothStatusUI(bluetoothController.getConnectionState());
        bluetoothController = BluetoothController.getInstance();
        bluetoothController.setBluetoothListener(bluetoothListener);
    }


    /**
     * Method for finding UI components and setting their event handlers
     */
    private void setupUI() {
        // Set up all UI element variables **********************
        bluetoothStatus = findViewById(R.id.txtBluetoothStatus);
        speedText = findViewById(R.id.txtSpeedValue);
        durationText = findViewById(R.id.txtDurationValue);
        messageText = findViewById(R.id.editMessage);
        Button sendButton = findViewById(R.id.btnSendMessage);
        Button forwardButton = findViewById(R.id.btnForward);
        Button backwardButton = findViewById(R.id.btnBackward);
        Button stopButton = findViewById(R.id.btnStop);
        distanceModeCheckBox = findViewById(R.id.checkMoveMode);
        TextView speedLabel = findViewById(R.id.txtSetSpeed);
        spinDurationLabel = findViewById(R.id.txtSetDuration);

        reconnectButton = findViewById(R.id.btnReconnect);

        SeekBar speedBar = findViewById(R.id.seekBarSpeed);
        speedBar.setMax(MAX_SPEED);
        durationBar = findViewById(R.id.seekBarDuration);
        durationBar.setMax(MAX_DURATION);

        boxA = findViewById(R.id.boxA);
        boxB = findViewById(R.id.boxB);
        boxC = findViewById(R.id.boxC);
        boxD = findViewById(R.id.boxD);
        // *********************************************************
        // *********************************************************

        // Set thumb color of both bars to white
        ShapeDrawable thumb = new ShapeDrawable(new OvalShape());
        thumb.getPaint().setColor(getResources().getColor(R.color.colorWhite));
        thumb.setIntrinsicHeight(40);
        thumb.setIntrinsicWidth(40);

        // We need another thumb object or moving one slider, will also move the other's thumb
        // if we give them the same thumb object
        ShapeDrawable thumb2 = new ShapeDrawable(new OvalShape());
        thumb2.getPaint().setColor(getResources().getColor(R.color.colorWhite));
        thumb2.setIntrinsicHeight(40);
        thumb2.setIntrinsicWidth(40);

        speedBar.setThumb(thumb);
        durationBar.setThumb(thumb2);

        // Listeners for seek bars that update their respective speed and duration EditTexts
        speedBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                speedText.setText(String.valueOf(progress));
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });

        durationBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                durationText.setText(String.valueOf(progress));
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {

            }
        });
        // ***********************************************************
        // ***********************************************************


        // Set listeners for all buttons
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bluetoothController.write(messageText.getText().toString().getBytes());
            }
        });

        forwardButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendMoveCommand(true);
            }
        });

        backwardButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendMoveCommand(false);
            }
        });

        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                messageSender.sendCommand(new Stop(null));
            }
        });

        reconnectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Only retry if we're not already connected
                if (bluetoothController.getConnectionState() != 3)
                    bluetoothController.connect(TARGET_MAC);
            }
        });
        // ***********************************************************
        // ***********************************************************

        // For both speed & duration edit texts, if they're set higher than their max values
        // set them both back to their max
        speedText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
            }

            @Override
            public void afterTextChanged(Editable s) {
                try {
                    int value = Integer.valueOf(s.toString());
                    if (value > MAX_SPEED)
                        speedText.setText(String.valueOf(MAX_SPEED));
                } catch (NumberFormatException e) {
                    // it's fine, just means string is empty "" or user somehow pasted non
                    // numeric characters in
                }
            }
        });

        durationText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
            }

            @Override
            public void afterTextChanged(Editable s) {
                try {
                    int value = Integer.valueOf(s.toString());

                    if (!distanceModeCheckBox.isChecked() && value > MAX_DURATION)
                        speedText.setText(String.valueOf(MAX_DURATION));
                    else if (distanceModeCheckBox.isChecked() && value > MAX_DISTANCE)
                        speedText.setText(String.valueOf(MAX_DISTANCE));
                } catch (NumberFormatException e) {
                    // it's fine, just means string is empty "" or user somehow pasted non
                    // numeric characters in
                }
            }
        });
        // ***********************************************************
        // ***********************************************************

        distanceModeCheckBox.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (distanceModeCheckBox.isChecked()) {
                    spinDurationLabel.setText(getString(R.string.txtSetDistance));
                    durationBar.setMax(MAX_DISTANCE);
                } else {
                    spinDurationLabel.setText(getString(R.string.txtSetDuration));
                    durationBar.setMax(MAX_DURATION);
                }
            }
        });


        // OUTPUT SOCKET SPINNER
        Spinner outputSocketSpinner = findViewById(R.id.spinnerOutSocket);
// Create an ArrayAdapter using the string array and a default spinner layout
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.output_socket_array, R.layout.spinner);
// Specify the layout to use when the list of choices appears
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
// Apply the adapter to the spinner
        outputSocketSpinner.setAdapter(adapter);

    }

    /**
     * Send move command (message) to EV3 brick
     *
     * @param forward True if motor to move forwards, false for backwards
     */
    private void sendMoveCommand(boolean forward) {
        // Set direction multiplier to 1 if forward = true, -1 otherwise (we're going backwards)
        int directionMultiplier = forward ? 1 : -1;

        OutputPort[] outputPorts = getSelectedPorts();

        if (outputPorts.length > 0) {
            // Store speed and duration values as ints
            int speedValue = Integer.valueOf(speedText.getText().toString());
            int durationValue = Integer.valueOf(durationText.getText().toString());


            if (!distanceModeCheckBox.isChecked()) {
                // Only send message to EV3 if speed and duration values are valid ("safe")
                if (speedValue > 0 && speedValue <= MAX_SPEED) {
                    if (durationValue > 0 && durationValue <= MAX_DURATION) {
                        messageSender.sendCommand(new Move(speedValue * directionMultiplier, durationValue, outputPorts));
                    } else {
                        Toast.makeText(DevActivity.super.getApplicationContext(), "ERROR: Duration must be > 0 and less than " + MAX_DURATION + "ms", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(DevActivity.super.getApplicationContext(), "ERROR: Speed must be > 0 and less than " + MAX_SPEED, Toast.LENGTH_SHORT).show();
                }
            } else {
                // Only send message to EV3 if speed and distance values are valid ("safe")
                if (speedValue > 0 && speedValue <= MAX_SPEED) {
                    if (durationValue > 0 && durationValue <= MAX_DURATION) {
                        messageSender.sendCommand(new MoveDist(outputPorts, (float) durationValue / 10 * directionMultiplier, speedValue));
                    } else {
                        Toast.makeText(DevActivity.super.getApplicationContext(), "ERROR: Distance must be > 0 and less than " + MAX_DISTANCE + "cm", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(DevActivity.super.getApplicationContext(), "ERROR: Speed must be > 0 and less than " + MAX_SPEED, Toast.LENGTH_SHORT).show();
                }
            }
        } else {
            Toast.makeText(this.getApplicationContext(), "Select at least one output port", Toast.LENGTH_SHORT).show();
        }

    }

    private OutputPort[] getSelectedPorts() {
        ArrayList<OutputPort> ports = new ArrayList<>();

        if (boxA.isChecked())
            ports.add(OutputPort.A);

        if (boxB.isChecked())
            ports.add(OutputPort.B);

        if (boxC.isChecked())
            ports.add(OutputPort.C);

        if (boxD.isChecked())
            ports.add(OutputPort.D);

        return ports.toArray(new OutputPort[]{});
    }

    /**
     * Updates connection status text and hides/shows reconnect button
     *
     * @param state State of bluetooth connection
     */
    private void updateBluetoothStatusUI(int state) {
        final int stringResId;
        final int colorResId;
        final int reconnectButtonVisibility;

        switch (state) {
            case State.STATE_CONNECTED:
                stringResId = R.string.txtBluetoothConnected;
                Log.d(TAG, "Connected");
                colorResId = R.color.colorBluetoothConnected;
                reconnectButtonVisibility = View.INVISIBLE;
                break;
            case State.STATE_DISCONNECTED:
                stringResId = R.string.txtBluetoothDisconnected;
                Log.d(TAG, "Disconnected");
                colorResId = R.color.colorBluetoothDisconnected;
                reconnectButtonVisibility = View.VISIBLE;
                break;
            case State.STATE_CONNECTING:
                stringResId = R.string.txtBluetoothConnecting;
                Log.d(TAG, "Connecting");
                colorResId = R.color.colorBluetoothConnecting;
                reconnectButtonVisibility = View.INVISIBLE;
                break;
            default:
                stringResId = R.string.txtBluetoothDisconnected;
                Log.d(TAG, "Disconnected");
                colorResId = R.color.colorBluetoothDisconnected;
                reconnectButtonVisibility = View.VISIBLE;
        }

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                bluetoothStatus.setText(stringResId);
                bluetoothStatus.setTextColor(getResources().getColor(colorResId));
                reconnectButton.setVisibility(reconnectButtonVisibility);
            }
        });

    }

    public static BluetoothController getBluetoothController() {
        return bluetoothController;
    }

    @Override
    protected void onDestroy() {
        Log.d(TAG, "onDestroy()");
        super.onDestroy();
        if (bluetoothController.isAvailable()) {
            if (bluetoothController.getConnectionState() == State.STATE_CONNECTED) {
                bluetoothController.disconnect();
            }

            bluetoothController.release();
        }
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
    }
}

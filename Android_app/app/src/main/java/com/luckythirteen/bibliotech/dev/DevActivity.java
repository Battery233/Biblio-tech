package com.luckythirteen.bibliotech.dev;

import android.bluetooth.BluetoothDevice;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.luckythirteen.bibliotech.R;

import java.util.UUID;

import co.lujun.lmbluetoothsdk.BluetoothController;
import co.lujun.lmbluetoothsdk.base.BluetoothListener;

import static android.bluetooth.BluetoothAdapter.STATE_CONNECTING;


public class DevActivity extends AppCompatActivity
{

    private static final String TAG = "DevActivity";
    private static final String TARGET_MAC = "AC:FD:CE:2B:82:F1";

    private TextView bluetoothStatus, messageReceived;
    private EditText messageText;
    private Button buttonSendMsg;

    private BluetoothController bluetoothController;
    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");


    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        Log.d(TAG, "onCreate()");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dev);

        bluetoothStatus = (TextView) findViewById(R.id.txtBluetoothStatus);
        messageReceived = (TextView) findViewById(R.id.txtMsgReceived);
        messageText = (EditText) findViewById(R.id.editMessage);
        buttonSendMsg = (Button) findViewById(R.id.btnSendMessage);

        buttonSendMsg.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View v)
            {
                Log.d(TAG, "write: " + messageText.getText().toString());
                bluetoothController.write(messageText.getText().toString().getBytes());
            }
        });

        // For classic bluetooth
        bluetoothController = BluetoothController.getInstance().build(this);
        bluetoothController.setAppUuid(MY_UUID);
        bluetoothController.connect(TARGET_MAC);

        bluetoothController.setBluetoothListener(new BluetoothListener()
        {
            @Override
            public void onReadData(BluetoothDevice device, byte[] data)
            {
                final String msg = new String(data);
                Log.d(TAG, "Received: " + msg);

                runOnUiThread(new Runnable()
                {
                    @Override
                    public void run()
                    {
                        messageReceived.setText(msg);

                    }
                });

                if (Build.VERSION.SDK_INT >= 26)
                {
                    ((Vibrator) getSystemService(VIBRATOR_SERVICE)).vibrate(VibrationEffect.createOneShot(150, VibrationEffect.DEFAULT_AMPLITUDE));
                }
                else
                {
                    ((Vibrator) getSystemService(VIBRATOR_SERVICE)).vibrate(150);
                }

            }

            @Override
            public void onActionStateChanged(int preState, int state)
            {

            }

            @Override
            public void onActionDiscoveryStateChanged(String discoveryState)
            {

            }

            @Override
            public void onActionScanModeChanged(int preScanMode, int scanMode)
            {

            }

            @Override
            public void onBluetoothServiceStateChanged(int state)
            {
                Log.d(TAG, "BT STATE: " + state);
                updateStatusText(state);
            }

            @Override
            public void onActionDeviceFound(BluetoothDevice device, short rssi)
            {

            }
        });

    }

    /**
     * Updates connection status text
     * @param state State of bluetooth connection
     */
    private void updateStatusText(int state)
    {
        // CONNECTED CODE = 3
        if (state == 3)
        {
            bluetoothStatus.setText(getString(R.string.txtBluetoothConnected));
            bluetoothStatus.setTextColor(getResources().getColor(R.color.colorBluetoothConnected));
        }
        else if (state == STATE_CONNECTING)
        {
            bluetoothStatus.setText(getString(R.string.txtBluetoothConnecting));
            bluetoothStatus.setTextColor(getResources().getColor(R.color.colorBluetoothConnecting));
        }
        else
        {
            bluetoothStatus.setText(getString(R.string.txtBluetoothDisconnected));
            bluetoothStatus.setTextColor(getResources().getColor(R.color.colorBluetoothDisconnected));
        }
    }

    @Override
    protected void onDestroy()
    {
        super.onDestroy();
        if (bluetoothController.isAvailable())
        {
            bluetoothController.release();
        }
    }


}


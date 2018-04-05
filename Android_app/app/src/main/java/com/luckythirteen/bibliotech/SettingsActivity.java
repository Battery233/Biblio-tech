package com.luckythirteen.bibliotech;

import android.annotation.SuppressLint;
import android.support.v7.app.AlertDialog;
import android.app.Dialog;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.os.Bundle;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.text.InputFilter;
import android.text.InputType;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.luckythirteen.bibliotech.brickapi.MessageSender;
import com.luckythirteen.bibliotech.brickapi.obj.LogEntry;
import com.luckythirteen.bibliotech.storage.UserPrefsManager;

import java.util.ArrayList;
import java.util.UUID;

import co.lujun.lmbluetoothsdk.BluetoothController;
import co.lujun.lmbluetoothsdk.base.BluetoothListener;
import co.lujun.lmbluetoothsdk.base.State;

public class SettingsActivity extends AppCompatActivity {

    private UserPrefsManager userPrefsManager;

    private EditText textMacAddress;
    private TextView bluetoothStatus, intervalText;
    private ImageButton reconnectButton;
    private Button setInterval, viewLogs;


    //public static final String EV33_MAC = "AC:FD:CE:2B:82:F1"; // COLIN'S
    private static final String EV33_MAC = "B0:B4:48:76:E7:86";
    private static final String EV13_MAC = "B0:B4:48:76:A2:C9";
    private static final String RPI_MAC = "B8:27:EB:04:8B:94";

    private static final String TAG = "SettingsActivity";

    // BluetoothController object for creating a connection to the EV3
    private static BluetoothController bluetoothController;

    // UUID of bluetooth connection (must be set the same on the EV3 bluetooth server)
    public static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    private MessageSender messageSender;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        userPrefsManager = new UserPrefsManager(this.getApplicationContext());
        setupUI();

        // For classic bluetooth
        bluetoothController = BluetoothController.getInstance().build(this);
        bluetoothController.setAppUuid(MY_UUID);

        bluetoothController.setBluetoothListener(bluetoothListener);
        bluetoothController.connect(SettingsActivity.RPI_MAC);

        messageSender = new MessageSender(bluetoothController);

    }

    private final BluetoothListener bluetoothListener = new BluetoothListener() {
        @Override
        public void onReadData(BluetoothDevice device, byte[] data) {
            Log.d(TAG, "Received: " + new String(data));
            JsonElement jsonElement = new JsonParser().parse(new String(data));
            JsonObject jsonObject = jsonElement.getAsJsonObject();

            if (jsonObject.has("scan_interval")) {
                jsonObject = jsonObject.getAsJsonObject("scan_interval");
                JsonPrimitive jsonPrimitive = jsonObject.getAsJsonPrimitive("interval");
                final String interval = jsonPrimitive.getAsString();

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        intervalText.setInputType(InputType.TYPE_CLASS_NUMBER);
                        intervalText.setFilters(new InputFilter[]{new InputFilter.LengthFilter(3)});
                        intervalText.setText(interval);
                    }
                });
            } else if (jsonObject.has("logs")) {
                Log.d(TAG, new String(data));
                ArrayList<LogEntry> logEntries = getLogEntries(new String(data));

                if (logEntries != null) {
                    showLogs(logEntries);
                } else {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Context context = SettingsActivity.super.getApplicationContext();
                            Toast.makeText(context, "Logs are empty!", Toast.LENGTH_SHORT).show();
                        }
                    });
                }
            } else {
                Log.w(TAG, "Unrecognised JSON received from RPi");
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
            if (state == State.STATE_CONNECTED) {
                messageSender.sendMessage("{\"get_scan_interval\":{}}");
            }
            Log.d(TAG, "BT STATE: " + state);
            updateBluetoothStatusUI(state);
        }

        @Override
        public void onActionDeviceFound(BluetoothDevice device, short rssi) {

        }
    };

    private void showLogs(ArrayList<LogEntry> logEntries) {

        final ArrayList<LogEntry> logEntries2 = logEntries;
        final Context context = this;
        final SettingsActivity fetchActivity = this;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Inflate dialog
                LayoutInflater layoutInflater = LayoutInflater.from(SettingsActivity.this);
                @SuppressLint("InflateParams") View wordsPrompt = layoutInflater.inflate(R.layout.dialog_loglist, null);
                Button clearLogs = wordsPrompt.findViewById(R.id.btnClearLogs);

                clearLogs.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        boolean success = messageSender.sendMessage("{\"clear_logs\":{}}");
                        String msg = "";

                        if(success)
                        {
                            msg = "Cleared logs";
                        }
                        else
                        {
                            msg = "Failed to clear logs";
                        }

                        Toast.makeText(SettingsActivity.super.getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
                    }
                });

                AlertDialog.Builder promptBuilder = new AlertDialog.Builder(SettingsActivity.this, R.style.AlertDialogTheme);
                promptBuilder.setView(wordsPrompt);

                final AlertDialog ad = promptBuilder.show();
                Log.w(TAG, "populateListView() - updating found words view");
                LogsArrayAdapter listAdapter = new LogsArrayAdapter(context, logEntries2, ad, fetchActivity);
                ListView listView = wordsPrompt.findViewById(R.id.lstBooks);

                // Set ListView to use updated listAdapter
                listView.setAdapter(listAdapter);
            }
        });

    }

    private ArrayList<LogEntry> genFakeLogs() {
        String[] ISBNs = {"1784987216283", "1324567897321", "1234567890647", "9856433921323", "0954326784212", "4372896409852"};
        String[] titles = {"Big data on toast sfdsfdfggf", "The Castle", "Wealth of Nations", "Steve Jobs", "Dirk Gently", "Harry Potter and the Chamber of Secrets"};
        String[] pos = {"0", "5", "3", "2", "1", "4"};

        ArrayList<LogEntry> fakeEntries = new ArrayList<>();

        for(int i = 0; i < ISBNs.length; i++)
        {
            fakeEntries.add(new LogEntry(ISBNs[i], titles[i], pos[i]));
        }

        return fakeEntries;
    }

    private String genString(ArrayList<LogEntry> logs)
    {
        StringBuilder s = new StringBuilder();
        for(LogEntry e : logs)
        {
            s.append(e.getISBN() + "\t" + e.getTitle() + e.getPos() + "\n");
        }

        return s.toString();
    }


    private ArrayList<LogEntry> getLogEntries(String s) {
        JsonParser jsonParser = new JsonParser();
        JsonElement jsonElement = jsonParser.parse(s);

        ArrayList<LogEntry> temp = new ArrayList<>();

        if (jsonElement.isJsonObject()) {
            try {
                JsonObject jsonObject = jsonElement.getAsJsonObject();
                JsonArray logs = jsonObject.getAsJsonArray("logs");

                for (JsonElement e : logs) {
                    JsonObject log = e.getAsJsonObject();
                    LogEntry logEntry = new LogEntry(log.get("ISBN").getAsString(), log.get("title").getAsString(), log.get("pos").getAsString());
                    temp.add(logEntry);
                }

                System.out.println("----------LOG ENTRIES------------------");
                for (LogEntry e : temp) {
                    System.out.println(String.format("%s\n%s\n%s\n\n", e.getISBN(), e.getTitle(), e.getTitle()));
                }

                return temp;
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        } else {
            Log.w(TAG, "Error in getLogEntries()");
            return null;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume()");
        updateBluetoothStatusUI(bluetoothController.getConnectionState());
        bluetoothController = BluetoothController.getInstance();
        bluetoothController.setBluetoothListener(bluetoothListener);
    }

    private void setupUI() {
        Button buttonEV13 = findViewById(R.id.btnEV13);
        Button buttonEV33 = findViewById(R.id.btnEV33);
        Button buttonRPI = findViewById(R.id.btnRPI);
        Button buttonSave = findViewById(R.id.btnSaveChanges);

        viewLogs = findViewById(R.id.btnViewLogs);
        intervalText = findViewById(R.id.txtInterval);
        setInterval = findViewById(R.id.btnSetInterval);

        textMacAddress = findViewById(R.id.editMac);
        textMacAddress.setText(userPrefsManager.getMacAddress());
        textMacAddress.setInputType(InputType.TYPE_NULL);

        bluetoothStatus = findViewById(R.id.txtBluetoothStatus);
        reconnectButton = findViewById(R.id.btnReconnect);

        intervalText.setInputType(InputType.TYPE_NULL);

        buttonEV13.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadNewMac(EV13_MAC);
                saveNewMac(textMacAddress.getText().toString());
            }
        });

        buttonEV33.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadNewMac(EV33_MAC);
                saveNewMac(textMacAddress.getText().toString());
            }
        });

        buttonRPI.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadNewMac(RPI_MAC);
                saveNewMac(textMacAddress.getText().toString());
            }
        });

        buttonSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                saveNewMac(textMacAddress.getText().toString());
            }
        });

        final Context context = this.getApplicationContext();
        setInterval.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newInterval = intervalText.getText().toString();
                String message = String.format("{\"set_scan_interval\":{\"interval\":%s}}", newInterval);
                messageSender.sendMessage(message);
                Toast.makeText(context, "Updated interval!", Toast.LENGTH_SHORT).show();

            }
        });

        reconnectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Only retry if we're not already connected
                if (bluetoothController.getConnectionState() != 3)
                    bluetoothController.connect(SettingsActivity.RPI_MAC);
            }
        });

        viewLogs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v)
            {
                if(bluetoothController.getConnectionState() == State.STATE_CONNECTED) {
                    messageSender.sendMessage("{\"get_logs\":{}}");
                }
                else
                {
                    Toast.makeText(SettingsActivity.super.getApplicationContext(), "Not connected to robot", Toast.LENGTH_SHORT).show();
                }

            }
        });
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

    private void loadNewMac(String mac) {
        textMacAddress.setText(mac);
    }

    private void saveNewMac(String mac) {
        userPrefsManager.updateMacAddress(mac);
        textMacAddress.setText(userPrefsManager.getMacAddress());

        if (mac.equals(userPrefsManager.getMacAddress())) {
            Toast.makeText(this, getString(R.string.msgSaveSuccessful), Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, getString(R.string.msgSaveUnsuccessful), Toast.LENGTH_SHORT).show();
        }

        Vibrator vib = (Vibrator) getSystemService(VIBRATOR_SERVICE);

        try {
            if (vib != null && vib.hasVibrator())
                vib.vibrate(100);
        } catch (NullPointerException e) {
            Log.d("settings", "vibrate error");
        }
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        try {
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
        } catch (Exception ignored) {
        }
    }
}

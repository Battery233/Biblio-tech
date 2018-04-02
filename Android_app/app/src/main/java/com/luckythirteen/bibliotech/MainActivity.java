package com.luckythirteen.bibliotech;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.text.InputFilter;
import android.text.InputType;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.demo.FetchActivity;
import com.luckythirteen.bibliotech.dev.DevActivity;
import com.luckythirteen.bibliotech.storage.UserPrefsManager;

import java.lang.reflect.Array;
import java.util.Objects;

/**
 * Activity essentially for selecting demo mode (retrieve book)
 * or dev mode (sending specific commands to the robot i.e. move by this much/to this position)
 * AND for performing any setup needed before communicating with the robot
 */

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";

    // Arbitrary request code meaning the bluetooth request came from pressing the 'Dev mode' button
    private static final int DEV_REQUEST_ENABLE_BT = 1;

    // Bluetooth request code for demo mode button
    private static final int DEMO_REQUEST_ENABLE_BT = 2;

    // Buttons on screen
    private Button demoButton;
    private Button devButton;
    private UserPrefsManager userPrefsManager;
    private boolean admin = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        userPrefsManager = new UserPrefsManager(this.getApplicationContext());

        if (!admin) {
            TextView text = findViewById(R.id.textView2);
            String guest = "guest";
            text.setText(guest);
        } else {
            TextView text = findViewById(R.id.textView2);
            String admin = "admin";
            text.setText(admin);
        }
        // Attach listener to demo button to load the "fetch book" activity
        demoButton = findViewById(R.id.btnDemoMode);
        demoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Only start dev activity if bluetooth is on
                if (bluetoothOn(DEMO_REQUEST_ENABLE_BT)) {
                    Intent intent = new Intent(MainActivity.super.getApplicationContext(), FetchActivity.class);
                    startActivity(intent);
                    try {
                        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
                    } catch (Exception ignored) {
                    }
                }
            }
        });


        // Attach listener to demo button to load the "dev mode" activity
        devButton = findViewById(R.id.btnDevMode);
        devButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (admin) {
                    if (!userPrefsManager.getMacAddress().equals("B8:27:EB:04:8B:94")) {
                        // Only start dev activity if bluetooth is on
                        if (bluetoothOn(DEV_REQUEST_ENABLE_BT)) {
                            Intent intent = new Intent(MainActivity.super.getApplicationContext(), DevActivity.class);
                            startActivity(intent);
                            try {
                                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
                            } catch (Exception ignored) {
                            }
                        }
                    } else {
                        Toast.makeText(getApplicationContext(), "Cannot run dev_mode on RPI\nGo settings and change MAC address", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(getApplicationContext(), "Dev mode is for admin only!\nplease login as admin first", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    /**
     * Returns true if bluetooth is on, false otherwise (but can also just start the activity if it's off and user successfully enables it after prompt)
     *
     * @param requestCode Request code (DEMO OR DEV)
     * @return True if bluetooth is already on, false otherwise
     */
    private boolean bluetoothOn(int requestCode) {
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        if (bluetoothAdapter != null) {
            // If bluetooth is not enabled ask for it, otherwise return true
            if (!bluetoothAdapter.isEnabled()) {
                Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                startActivityForResult(enableBtIntent, requestCode);
                return false;
            } else {
                return true;
            }
        } else {
            Toast.makeText(getApplicationContext(), "Your device does not support bluetooth!", Toast.LENGTH_LONG).show();
            return false;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        Log.d(TAG, "Request code: " + requestCode);

        switch (requestCode) {
            // Case when request came from pressing DEV mode button
            case DEV_REQUEST_ENABLE_BT:
                if (resultCode == Activity.RESULT_OK) {
                    // User enabled bluetooth so simulate them pressing the dev mode button
                    devButton.performClick();
                } else {
                    Toast.makeText(getApplicationContext(), "Bluetooth is required to continue!", Toast.LENGTH_LONG).show();
                }
                break;

            // Case when request came from pressing DEMO mode button
            case DEMO_REQUEST_ENABLE_BT:
                if (resultCode == Activity.RESULT_OK) {
                    // User enabled bluetooth so simulate them pressing the demo mode button
                    demoButton.performClick();
                } else {
                    Toast.makeText(getApplicationContext(), "Bluetooth is required to continue!", Toast.LENGTH_LONG).show();
                }
                break;
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {

        if (item.getItemId() == R.id.action_account) {
            if (admin) {
                AlertDialog.Builder alertDialog = new AlertDialog.Builder(MainActivity.this, R.style.AlertDialogTheme);
                alertDialog.setTitle("Log out, admin?");
                alertDialog.setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        admin = false;
                        TextView text = findViewById(R.id.textView2);
                        String guest = "guest";
                        text.setText(guest);
                    }
                });
                alertDialog.setNegativeButton("cancel", null);
                alertDialog.show();
            }else{
                final EditText input = new EditText(this);
                input.setGravity(Gravity.CENTER);
                input.setHint("Input password:");
                input.setHintTextColor(getResources().getColor(R.color.colorAccent));
                input.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
                input.setFilters(new InputFilter[] { new InputFilter.LengthFilter(10)});
                AlertDialog.Builder alertDialog = new AlertDialog.Builder(MainActivity.this, R.style.AlertDialogTheme);
                alertDialog.setTitle("Log in as admin?");
                alertDialog.setView(input);
                alertDialog.setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String inputPassword = input.getText().toString();
                        if(Objects.equals(inputPassword, "")){
                            Toast.makeText(MainActivity.super.getApplicationContext(), "You really need to input something!", Toast.LENGTH_SHORT).show();
                        }else if(Objects.equals(inputPassword,"brownie")||Objects.equals(inputPassword,"Brownie")){
                            admin = true;
                            TextView text = findViewById(R.id.textView2);
                            String admin = "admin";
                            text.setText(admin);
                            Toast.makeText(MainActivity.super.getApplicationContext(), "Login success!", Toast.LENGTH_SHORT).show();
                        }else{
                            Toast.makeText(MainActivity.super.getApplicationContext(), "Wrong password!", Toast.LENGTH_SHORT).show();
                        }
                    }
                });
                alertDialog.setNegativeButton("cancel", null);
                alertDialog.show();
            }

            return true;
        }
        if (item.getItemId() == R.id.action_settings) {
            if (admin) {
                Intent intent = new Intent(MainActivity.super.getApplicationContext(), SettingsActivity.class);
                startActivity(intent);
                try {
                    overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
                } catch (Exception ignored) {
                }
            } else {
                Toast.makeText(this, "Advanced settings is for admin only!", Toast.LENGTH_SHORT).show();
            }
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}

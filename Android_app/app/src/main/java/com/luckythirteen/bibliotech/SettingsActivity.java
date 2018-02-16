package com.luckythirteen.bibliotech;

import android.os.VibrationEffect;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.storage.UserPrefsManager;

public class SettingsActivity extends AppCompatActivity {

    private UserPrefsManager userPrefsManager;

    private EditText textMacAddress;
    private Button buttonEV13, buttonEV33, buttonSave;

    public static final String EV33_MAC = "AC:FD:CE:2B:82:F1";
    public static final String EV13_MAC = "B0:B4:48:76:A2:C9";


    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        userPrefsManager = new UserPrefsManager(this.getApplicationContext());
        setupUI();

    }

    private void setupUI()
    {
        textMacAddress = findViewById(R.id.editMac);
        buttonEV13 = findViewById(R.id.btnEV13);
        buttonEV33 = findViewById(R.id.btnEV33);
        buttonSave = findViewById(R.id.btnSaveChanges);

        textMacAddress.setText(userPrefsManager.getMacAddress());

        buttonEV13.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadNewMac(EV13_MAC);
            }
        });

        buttonEV33.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
               loadNewMac(EV33_MAC);
            }
        });

        buttonSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                saveNewMac(textMacAddress.getText().toString());
            }
        });

    }

    private void loadNewMac(String mac)
    {
        textMacAddress.setText(mac);
    }

    private void saveNewMac(String mac)
    {
        userPrefsManager.updateMacAddress(mac);
        textMacAddress.setText(userPrefsManager.getMacAddress());

        if(mac.equals(userPrefsManager.getMacAddress()))
        {
            Toast.makeText(this, getString(R.string.msgSaveSuccessful), Toast.LENGTH_SHORT).show();
        }
        else
        {
            Toast.makeText(this, getString(R.string.msgSaveUnsuccessful), Toast.LENGTH_SHORT).show();
        }

        Vibrator vib = (Vibrator) getSystemService(VIBRATOR_SERVICE);

        if(vib.hasVibrator())
            vib.vibrate(100);
    }
}

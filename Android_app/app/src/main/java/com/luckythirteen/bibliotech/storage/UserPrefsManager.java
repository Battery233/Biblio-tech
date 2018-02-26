package com.luckythirteen.bibliotech.storage;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Used to read/write to persistent storage
 */

public class UserPrefsManager {
    private static final String TAG = "UserPrefsManager";
    private static final String APP_KEY = "app_info";

    private static final String DEFAULT_MAC = "B0:B4:48:76:E7:86"; // EV33

    private Context context;
    private SharedPreferences sharedPrefs;

    public UserPrefsManager(Context context) {
        this.context = context;
        this.sharedPrefs = this.context.getSharedPreferences(APP_KEY, Context.MODE_PRIVATE);
    }

    /**
     * Updates MAC address stored
     *
     * @param mac New MAC address
     */
    public void updateMacAddress(String mac) {
        SharedPreferences.Editor editor = sharedPrefs.edit();
        editor.putString(StorageKeys.MAC_ADDRESS.name(), mac);
        editor.commit();
    }

    /**
     * Get the currently saved MAC address
     *
     * @return The MAC address
     */
    public String getMacAddress() {
        return sharedPrefs.getString(StorageKeys.MAC_ADDRESS.name(), DEFAULT_MAC);
    }


}

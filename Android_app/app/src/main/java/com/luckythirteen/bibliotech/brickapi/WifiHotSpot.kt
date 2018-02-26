package com.luckythirteen.bibliotech.brickapi

/**
 * Created by great on 2018/2/26.
 * Try to fix the wifi hotspot bug
 */

import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method

import android.content.Context
import android.net.wifi.WifiConfiguration
import android.net.wifi.WifiManager

class WifiHotUtil(context: Context) {

    private var mWifiManager: WifiManager? = null

    private var mContext: Context? = null

    val isWifiApEnabled: Boolean
        get() {
            try {
                val method = mWifiManager!!.javaClass.getMethod("isWifiApEnabled")
                method.isAccessible = true
                return method.invoke(mWifiManager) as Boolean
            } catch (e: NoSuchMethodException) {
                e.printStackTrace()
            } catch (e: Exception) {
                e.printStackTrace()
            }

            return false
        }

    init {
        mContext = context
        mWifiManager = mContext!!.getSystemService(Context.WIFI_SERVICE) as WifiManager
    }

    fun startWifiAp(ssid: String, passwd: String) {
        if (mWifiManager!!.isWifiEnabled) {
            mWifiManager!!.isWifiEnabled = false
        }

        if (!isWifiApEnabled) {
            stratWifiAp(ssid, passwd)
        }
    }

    /**
     * @param mSSID
     * @param mPasswd
     */
    private fun stratWifiAp(mSSID: String, mPasswd: String) {
        var method1: Method? = null
        try {
            method1 = mWifiManager!!.javaClass.getMethod("setWifiApEnabled",
                    WifiConfiguration::class.java,Boolean::class.javaPrimitiveType)
            val netConfig = WifiConfiguration()

            netConfig.SSID = mSSID
            netConfig.preSharedKey = mPasswd

            netConfig.allowedAuthAlgorithms.set(WifiConfiguration.AuthAlgorithm.OPEN)
            netConfig.allowedProtocols.set(WifiConfiguration.Protocol.RSN)
            netConfig.allowedProtocols.set(WifiConfiguration.Protocol.WPA)
            netConfig.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK)
            netConfig.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.CCMP)
            netConfig.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.TKIP)
            netConfig.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.CCMP)
            netConfig.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.TKIP)
            method1!!.invoke(mWifiManager, netConfig, true)

        } catch (e: IllegalArgumentException) {
            e.printStackTrace()
        } catch (e: IllegalAccessException) {
            e.printStackTrace()
        } catch (e: InvocationTargetException) {
            e.printStackTrace()
        } catch (e: SecurityException) {
            e.printStackTrace()
        } catch (e: NoSuchMethodException) {
            e.printStackTrace()
        }

    }

    fun closeWifiAp() {
        val wifiManager = mContext!!.getSystemService(Context.WIFI_SERVICE) as WifiManager
        if (isWifiApEnabled) {
            try {
                val method = wifiManager.javaClass.getMethod("getWifiApConfiguration")
                method.isAccessible = true
                val config = method.invoke(wifiManager) as WifiConfiguration
                val method2 = wifiManager.javaClass.getMethod("setWifiApEnabled", WifiConfiguration::class.java, Boolean::class.javaPrimitiveType)
                method2.invoke(wifiManager, config, false)
            } catch (e: NoSuchMethodException) {
                e.printStackTrace()
            } catch (e: IllegalArgumentException) {
                e.printStackTrace()
            } catch (e: IllegalAccessException) {
                e.printStackTrace()
            } catch (e: InvocationTargetException) {
                e.printStackTrace()
            }

        }
    }

    companion object {
        val TAG = "WifiApAdmin"
    }

}
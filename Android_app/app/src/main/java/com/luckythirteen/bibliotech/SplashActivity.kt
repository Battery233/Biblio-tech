package com.luckythirteen.bibliotech

import android.annotation.SuppressLint
import android.content.DialogInterface
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.support.v7.app.AlertDialog
import android.support.v7.app.AppCompatActivity
import android.util.DisplayMetrics
import android.view.KeyEvent
import kotlinx.android.synthetic.main.activity_splash.*


class SplashActivity : AppCompatActivity() {

    private val tag = "Splash Activity"

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        //no action bar
        supportActionBar?.hide()

        val keyListener = DialogInterface.OnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_BACK && event.repeatCount == 0) {
                println(">>>>>[$tag] keyListener = true")
                true
            } else {
                println(">>>>>[$tag] keyListener = false")
                false
            }
        }

        //Test if the Screen resolution reached the requirement of at least 1280 Pixels in height, which most of current phone can reach this standard
        // the app requires at least 1280 or the ui will crash

        val metrics = DisplayMetrics()
        windowManager.defaultDisplay.getRealMetrics(metrics)

        println(">>>>>[$tag] heightPixels = ${metrics.heightPixels}")

        if (metrics.heightPixels < 1280) {

            val handler = Handler()

            val alert = AlertDialog.Builder(this)

            alert.setTitle("You can't run app on this device!")

            alert.setMessage("You need a device with at least 1280 heightPixels to use the app\nApp will quit in 10 seconds")

            alert.setOnKeyListener(keyListener).setCancelable(false)

            alert.show()

            handler.postDelayed({

                this.finish()

            }, 10000)

        } else {

            val packageInfoManager = packageManager

            try {
                //Show version number at bottom
                val pm = packageInfoManager.getPackageInfo("com.luckythirteen.bibliotech", 0)
                versionNumber.text = "Version:" + pm.versionName
            } catch (e: Exception) {
                e.printStackTrace()
            }

            val handler = Handler()
            //Delay 3seconds at splash activity
            handler.postDelayed({

                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
                try {
                    overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                } catch (e: Exception) {
                }

                //finish the activity and jump to main activity
                this.finish()
            }, 3000)
        }
    }

    override fun onBackPressed() {
        //disable back button here
    }
}

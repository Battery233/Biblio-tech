package com.luckythirteen.bibliotech

import android.annotation.SuppressLint
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.graphics.Typeface
import android.os.Handler
import android.content.Intent
import kotlinx.android.synthetic.main.activity_splash.*

class SplashActivity : AppCompatActivity() {

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        //no action bar
        supportActionBar?.hide()

        val typeface = Typeface.createFromAsset(assets, "fonts/comicbd.ttf")
        slogan.typeface = typeface

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

            //finish the activity and jump to main activity
            this.finish()
        }, 3000)
    }
}

package com.luckythirteen.bibliotech

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.graphics.Typeface
import android.os.Handler
import android.content.Intent
import kotlinx.android.synthetic.main.activity_splash.*

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)
        supportActionBar?.hide()
        val typeface = Typeface.createFromAsset(assets, "fonts/comicbd.ttf")
        slogan.typeface = typeface
        val handler = Handler()

        val packageInfoManager = packageManager
        try {
            val pm = packageInfoManager.getPackageInfo("com.luckythirteen.bibliotech", 0)           //Show version number at bottom
            versionNumber.text = "Version:" + pm.versionName
        } catch (e: Exception) {
            e.printStackTrace()
        }

        handler.postDelayed({
            val intent = Intent(this, MainActivity::class.java)               //Delay 3seconds at splash
            startActivity(intent)
            this.finish()
        }, 3000)
    }
}

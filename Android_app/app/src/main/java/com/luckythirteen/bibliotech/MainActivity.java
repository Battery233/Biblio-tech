package com.luckythirteen.bibliotech;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;

import com.luckythirteen.bibliotech.demo.FetchActivity;
import com.luckythirteen.bibliotech.dev.DevActivity;

/**
 * Activity essentially for selecting demo mode (retrieve book)
 * or dev mode (sending specific commands to the robot i.e. move by this much/to this position)
 * AND for performing any setup needed before communicating with the robot
 */

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Attach listener to demo button to load the "fetch book" activity
        Button demoButton = (Button) findViewById(R.id.btnDemoMode);
        demoButton.findViewById(R.id.btnDemoMode).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.super.getApplicationContext(), FetchActivity.class);
                startActivity(intent);
            }
        });

        // Attach listener to demo button to load the "dev mode" activity
        Button devButton = (Button) findViewById(R.id.btnDevMode);
        devButton.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View v)
            {
                Intent intent = new Intent(MainActivity.super.getApplicationContext(), DevActivity.class);
                startActivity(intent);
            }
        });

    }

}

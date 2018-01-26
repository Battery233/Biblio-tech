package com.luckythirteen.bibliotech.demo;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;

import com.luckythirteen.bibliotech.R;

import java.util.HashMap;

/**
 * This activity will be used by the end-user to send a retrieve book request to the robot
 * and is therefore the primary activity of the whole application.
 */

public class FetchActivity extends AppCompatActivity {

    /**
     * Debugging tag
     */
    private static final String TAG = "FetchActivity";

    /**
     * Placeholder HashMap that holds a database of books for testing UI functionality
     */
    private static HashMap<String, String> testBooks;

    /**
     * Stores strings of the currently typed title and author
     */
    private static String title, author;

    /**
     * Button for sending fetch message to robot
     */
    private Button getButton;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_demo_fetch);

        getButton = (Button) findViewById(R.id.btnGet);

        initialiseTestBooks();
        setTextViewAutocompletes();
    }

    /**
     * Populates the autocomplete suggestions for the title & author TextViews using (for now)
     * the mock book database (testBooks HashMap)
     */
    private void setTextViewAutocompletes() {
        // Populate suggestions for title text view
        ArrayAdapter<String> titleAdapter = new ArrayAdapter<String>(this, android.R.layout.simple_dropdown_item_1line, testBooks.keySet().toArray(new String[]{}));
        AutoCompleteTextView titleView = (AutoCompleteTextView) findViewById(R.id.autoTxtTitle);
        titleView.setAdapter(titleAdapter);

        titleView.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                title = s.toString();
                buttonCheck();
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

        // Populate suggestions for author text view
        ArrayAdapter<String> authorAdapter = new ArrayAdapter<String>(this, android.R.layout.simple_dropdown_item_1line, testBooks.values().toArray(new String[]{}));
        AutoCompleteTextView authorView = (AutoCompleteTextView) findViewById(R.id.autoTxtAuthor);
        authorView.setAdapter(authorAdapter);

        authorView.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                author = s.toString();
                buttonCheck();
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
    }

    /**
     * Hides or shows "get" button dependent on whether entered title and author combination are valid
     */
    private void buttonCheck() {
        if (testBooks.containsKey(title)) {
            if (testBooks.get(title).equals(author)) {
                getButton.setVisibility(View.VISIBLE);
            } else {
                getButton.setVisibility(View.INVISIBLE);
            }
        } else {
            getButton.setVisibility(View.INVISIBLE);
        }
    }

    /**
     * Placeholder method to populate "database" of books
     */
    private void initialiseTestBooks() {
        testBooks = new HashMap<>();
        testBooks.put("Animal Farm", "George Orwell");
        testBooks.put("Harry Potter and the Philosopher's Stone", "J. K. Rowling");
        testBooks.put("To Kill a Mockingbird", "Harper Lee");
        testBooks.put("The Great Gatsby", "F. Scott Fitzgerald");
        testBooks.put("The Da Vinci Code", "Dan Brown");
    }
}

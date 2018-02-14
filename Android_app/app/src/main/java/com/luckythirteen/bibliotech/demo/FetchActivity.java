package com.luckythirteen.bibliotech.demo;

import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.MessageSender;
import com.luckythirteen.bibliotech.brickapi.command.ReachBook;
import com.luckythirteen.bibliotech.brickapi.obj.Book;
import com.luckythirteen.bibliotech.dev.DevActivity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/**
 * This activity will be used by the end-user to send a retrieve book request to the robot
 * and is therefore the primary activity of the whole application.
 */

public class FetchActivity extends AppCompatActivity {

    /**
     * Debugging tag
     */
    private static final String TAG = "FetchActivity";


    private ArrayList<Book> books;

    private Button btnSelectBook, btnGetBook;
    private TextView authorLabel, titleLabel;
    private TextView titleTextView, authorTextView;

    private TextView helperText;
    private ImageView helperArrow;
    private Animation arrowAnim;

    private Book chosenBook;

    private boolean beenInitialisedBefore = false;
    private MessageSender messageSender;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        Log.d(TAG, "onCreate()");
        super.onCreate(savedInstanceState);

        if(!beenInitialisedBefore)
        {
            setContentView(R.layout.activity_demo_new);
            setupUI();
            books = getBooks();
            beenInitialisedBefore = true;
            messageSender = new MessageSender(DevActivity.getBluetoothController());
        }

    }

    private void setupUI()
    {
        btnSelectBook = findViewById(R.id.btnViewBooks);
        btnGetBook = findViewById(R.id.btnGet);
        helperArrow = findViewById(R.id.imgArrow);
        helperText = findViewById(R.id.txtSelectHelp);

        authorLabel = findViewById(R.id.txtAuthorLabel);
        titleLabel = findViewById(R.id.txtTitleLabel);
        titleTextView = findViewById(R.id.txtTitle);
        authorTextView = findViewById(R.id.txtAuthor);

        arrowAnim = AnimationUtils.loadAnimation(this.getApplicationContext(), R.anim.hover);
        helperArrow.startAnimation(arrowAnim);

        btnSelectBook.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v)
            {
                onSelectBookButton();
            }
        });
        btnGetBook.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View v)
            {
                onGetButton();
            }
        });
    }

    private void onSelectBookButton()
    {
        Log.d(TAG, "Select book button pressed");
        // Inflate dialog
        LayoutInflater layoutInflater = LayoutInflater.from(FetchActivity.this);
        View wordsPrompt = layoutInflater.inflate(R.layout.dialog_booklist, null);
        AlertDialog.Builder promptBuilder = new AlertDialog.Builder(FetchActivity.this, R.style.AlertDialogTheme);
        promptBuilder.setView(wordsPrompt);

        final AlertDialog ad = promptBuilder.show();
        populateListView(wordsPrompt, ad);
    }


    /**
     * Called back from the BookListArrayAdapter when the user selects a book
     * @param book The book they selected
     */
    public void onBookSelected(Book book)
    {
        Log.d(TAG, "Selected book with ISBN: " + book.getISBN());
        chosenBook = book;

        // Hide helper UI elements
        findViewById(R.id.imgArrow).clearAnimation(); // Needed otherwise won't disappear even with the line below
        helperArrow.setVisibility(View.GONE);
        helperText.setVisibility(View.GONE);


        // Show title and author UI elements
        authorLabel.setVisibility(View.VISIBLE);
        titleLabel.setVisibility(View.VISIBLE);
        authorTextView.setVisibility(View.VISIBLE);
        titleTextView.setVisibility(View.VISIBLE);
        btnGetBook.setVisibility(View.VISIBLE);

        // Set title and author text elements
        authorTextView.setText(chosenBook.getAuthor());
        titleTextView.setText(chosenBook.getTitle());
    }

    private void onGetButton()
    {
        Log.d(TAG, "onGetButton()");

        if(chosenBook != null)
        {
            Log.d(TAG, String.format("[FIND BOOK] \n ISBN: %s \n Title: %s \n Author: %s", chosenBook.getISBN(), chosenBook.getTitle(), chosenBook.getAuthor()));

            // Make sure MessageSender object initialised
            assert messageSender != null: "MessageSender object not initialised";

            // Send ReachBook command
            ReachBook reachBook = new ReachBook(chosenBook.getISBN());


            // Try to send message and store if worked or not
            boolean messageSuccess = messageSender.sendCommand(reachBook);

            if(messageSuccess)
                Toast.makeText(this.getApplicationContext(), "Waiting for robot...", Toast.LENGTH_LONG).show();
            else
                Toast.makeText(this.getApplicationContext(), "Failed to send message to robot :(", Toast.LENGTH_SHORT).show();




        }
        else
        {
            Log.e(TAG, "Get button is visible despite chosen book being NULL");
        }
    }

    /**
     * Populates the view containing the list of books
     * @param prompt The inner view we want to fill
     * @param ad The whole dialog (so we can close it later)
     */
    private void populateListView(View prompt, AlertDialog ad)
    {
        Log.w(TAG, "populateListView() - updating found words view");

        BookListArrayAdapter listAdapter = new BookListArrayAdapter(this, R.layout.list_books_row, getBooks(), ad, this);
        ListView listView = (ListView) prompt.findViewById(R.id.lstBooks);

        // Set ListView to use updated listAdapter
        listView.setAdapter(listAdapter);
    }


    /**
     * Dummy function that mimics receiving the list of books from the brick
     * (will be replaced eventually)
     * @return List of books
     */
    private ArrayList<Book> getBooks()
    {
        ArrayList<Book> books = new ArrayList<>();
        books.add(new Book("9781785782343" , "Big Data How the Information Revolution Is Transforming Our Lives", "Brian Clegg", true));
        books.add(new Book("9781447221098" , "Dirk Gently Holistic Detective Agency", "Douglas Adams", true));
        books.add(new Book("9780241197806" , "The Castle", "Franz Kafka", true));
        books.add(new Book("9781840226881", "Wealth of Nations", "Adam Smith", true));
        books.add(new Book("9780349140438", "Steve Jobs", "Walter Isaacson", true));
        books.add(new Book("9780140441185", "Thus Spoke Zarathustra", "Friedrich Nietzsche", false));

        return books;

    }
}

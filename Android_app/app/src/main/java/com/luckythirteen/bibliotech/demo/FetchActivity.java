package com.luckythirteen.bibliotech.demo;

import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.ListView;

import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.obj.Book;

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

    /**
     * Hashmap that holds the list of books sent from the brick
     * Key: ISBN
     * Value: Book object
     */
    private static HashMap<String, Book> books;

    private Button btnSelectBook;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_demo_new);

        generateBookMap();
        setupUI();

    }

    private void setupUI()
    {
        btnSelectBook = findViewById(R.id.btnViewBooks);

        btnSelectBook.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v)
            {
                onSelectBookButton();
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

    private void populateListView(View prompt, AlertDialog ad)
    {
        Log.w(TAG, "populateListView() - updating found words view");

        BookListArrayAdapter listAdapter = new BookListArrayAdapter(this, R.layout.list_books_row, getBooks(), ad);
        ListView listView = (ListView) prompt.findViewById(R.id.lstBooks);

        // Set ListView to use updated listAdapter
        listView.setAdapter(listAdapter);
    }

    /**
     * Generates the hashmap of books
     * @return Hashmap of books ISBN: Book
     */
    private void generateBookMap()
    {
        books = new HashMap<>();

        for(Book b : getBooks())
        {
            books.put(b.getISBN(), b);
        }
    }

    /**
     * Dummy function that mimics receiving the list of books from the brick
     * (will be replaced eventually)
     * @return List of books
     */
    private List<Book> getBooks()
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

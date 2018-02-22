package com.luckythirteen.bibliotech.demo;

import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.BuildConfig;
import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.MessageParser;
import com.luckythirteen.bibliotech.brickapi.MessageSender;
import com.luckythirteen.bibliotech.brickapi.command.QueryDB;
import com.luckythirteen.bibliotech.brickapi.command.ReachBook;
import com.luckythirteen.bibliotech.brickapi.command.TakeBook;
import com.luckythirteen.bibliotech.brickapi.messages.MessageType;
import com.luckythirteen.bibliotech.brickapi.obj.Book;
import com.luckythirteen.bibliotech.brickapi.obj.BookList;
import com.luckythirteen.bibliotech.dev.DevActivity;
import com.luckythirteen.bibliotech.storage.UserPrefsManager;

import java.util.ArrayList;

import co.lujun.lmbluetoothsdk.BluetoothController;
import co.lujun.lmbluetoothsdk.base.BluetoothListener;
import co.lujun.lmbluetoothsdk.base.State;

/**
 * This activity will be used by the end-user to send a retrieve book request to the robot
 * and is therefore the primary activity of the whole application.
 */

//TODO: WHOLE CLASS NEEDS SOME HANDLING FOR WHEN ROBOT IS BUSY

public class FetchActivity extends AppCompatActivity
{

    /**
     * Debugging tag
     */
    private static final String TAG = "FetchActivity";


    private ArrayList<Book> books;

    // UI Elements
    private Button btnSelectBook, btnGetBook;
    private TextView authorLabel, titleLabel, bluetoothStatus;
    private TextView titleTextView, authorTextView;
    private ImageButton reconnectButton;
    private TextView helperText;
    private ImageView helperArrow;
    private Animation arrowAnim;


    private Book chosenBook;

    private MessageSender messageSender;

    private BluetoothController bluetoothController;
    private static String targetMac;

    private final static String SHARED_PREFS_KEY = "APP_INFO";
    private final static String DEMO_ACTIVE_KEY = "demo_active";


    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        Log.d(TAG, "onCreate()");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_demo_new);
        setupUI();


        books = getBooks();

        // Use stored MAC address
        targetMac = new UserPrefsManager(this.getApplicationContext()).getMacAddress();


        // For classic bluetooth
        bluetoothController = BluetoothController.getInstance().build(this);
        bluetoothController.setAppUuid(DevActivity.MY_UUID);

        bluetoothController.setBluetoothListener(bluetoothListener);
        bluetoothController.connect(targetMac);

        messageSender = new MessageSender(BluetoothController.getInstance());
        updateBluetoothStatusUI(bluetoothController.getConnectionState());

    }

    /**
     * Updates connection status text and hides/shows reconnect button
     *
     * @param state State of bluetooth connection
     */
    private void updateBluetoothStatusUI(int state) {
        final int stringResId;
        final int colorResId;
        final int reconnectButtonVisibility;

        switch (state) {
            case State.STATE_CONNECTED:
                stringResId = R.string.txtBluetoothConnected;
                Log.d(TAG, "Connected");
                colorResId = R.color.colorBluetoothConnected;
                reconnectButtonVisibility = View.INVISIBLE;
                break;
            case State.STATE_DISCONNECTED:
                stringResId = R.string.txtBluetoothDisconnected;
                Log.d(TAG, "Disconnected");
                colorResId = R.color.colorBluetoothDisconnected;
                reconnectButtonVisibility = View.VISIBLE;
                break;
            case State.STATE_CONNECTING:
                stringResId = R.string.txtBluetoothConnecting;
                Log.d(TAG, "Connecting");
                colorResId = R.color.colorBluetoothConnecting;
                reconnectButtonVisibility = View.INVISIBLE;
                break;
            default:
                stringResId = R.string.txtBluetoothDisconnected;
                Log.d(TAG, "Disconnected");
                colorResId = R.color.colorBluetoothDisconnected;
                reconnectButtonVisibility = View.VISIBLE;
        }

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                bluetoothStatus.setText(stringResId);
                bluetoothStatus.setTextColor(getResources().getColor(colorResId));
                reconnectButton.setVisibility(reconnectButtonVisibility);
            }
        });

    }

    @Override
    protected void onResume()
    {
        super.onResume();
        Log.d(TAG, "onResume()");
        bluetoothController = BluetoothController.getInstance();
        bluetoothController.setBluetoothListener(bluetoothListener);

        if(bluetoothController.getConnectionState() != State.STATE_CONNECTED && bluetoothController.getConnectionState() != State.STATE_CONNECTING)
        {
            bluetoothController.connect(targetMac);
        }
    }

    @Override
    protected void onStop() {
        super.onStop();

        // Store our shared preference
        SharedPreferences sp = getSharedPreferences(SHARED_PREFS_KEY, MODE_PRIVATE);
        SharedPreferences.Editor ed = sp.edit();
        ed.putBoolean(DEMO_ACTIVE_KEY, false);
        ed.commit();
    }

    private void setupUI()
    {
        bluetoothStatus = findViewById(R.id.txtBluetoothStatus);
        reconnectButton = findViewById(R.id.btnReconnect);

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

        reconnectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Only retry if we're not already connected
                if (bluetoothController.getConnectionState() != 3)
                    bluetoothController.connect(targetMac);
            }
        });
    }

    /**
     * Shows list of books user can select
     */
    private void onSelectBookButton()
    {
        Log.d(TAG, "Select book button pressed");
        messageSender.sendCommand(new QueryDB(null));
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
     * Show view containing list of books
     * @param books List of books
     */
    private void showBookList(final ArrayList<Book> books)
    {
        final Context context = this;
        final FetchActivity fetchActivity = this;
        runOnUiThread(new Runnable()
        {
            @Override
            public void run()
            {
                // Inflate dialog
                LayoutInflater layoutInflater = LayoutInflater.from(FetchActivity.this);
                View wordsPrompt = layoutInflater.inflate(R.layout.dialog_booklist, null);
                AlertDialog.Builder promptBuilder = new AlertDialog.Builder(FetchActivity.this, R.style.AlertDialogTheme);
                promptBuilder.setView(wordsPrompt);

                final AlertDialog ad = promptBuilder.show();
                Log.w(TAG, "populateListView() - updating found words view");
                BookListArrayAdapter listAdapter = new BookListArrayAdapter(context, R.layout.list_books_row, books, ad, fetchActivity);
                ListView listView = (ListView) wordsPrompt.findViewById(R.id.lstBooks);

                // Set ListView to use updated listAdapter
                listView.setAdapter(listAdapter);


            }
        });



    }


    /**
     * Bluetooth event listener
     */
    private final BluetoothListener bluetoothListener = new BluetoothListener()
    {
        @Override
        public void onReadData(BluetoothDevice device, byte[] data)
        {
            Log.d(TAG, "Received: " + new String(data));
            String json = new String(data);
            MessageType type = MessageParser.determineMessageType(json);
            performAction(type, json);
        }

        @Override
        public void onActionStateChanged(int preState, int state)
        {

        }

        @Override
        public void onActionDiscoveryStateChanged(String discoveryState)
        {
        }

        @Override
        public void onActionScanModeChanged(int preScanMode, int scanMode)
        {

        }

        @Override
        public void onBluetoothServiceStateChanged(int state)
        {
            updateBluetoothStatusUI(state);
        }

        @Override
        public void onActionDeviceFound(BluetoothDevice device, short rssi)
        {

        }
    };

    /**
     * Performs an action based on the message received from the robot
     * @param type Type of the message
     * @param json The raw JSON message
     */
    private void performAction(MessageType type, String json)
    {
        if(type == MessageType.bookList)
        {
            showBookList(MessageParser.getBookListFromJson(json).getBooks());
        }
        else if(type == MessageType.foundBook)
        {
            showGetPrompt();
        }
        else if(type == MessageType.missingBook)
        {
            showMissingBookPrompt();
        }
        else if(type == MessageType.undefined)
        {
            Log.w(TAG, "Don't understand message: " + json);
        }
    }

    /**
     * Called when the robot has told the app the requested book is there
     */
    private void showMissingBookPrompt()
    {
        final Context context = this;
        runOnUiThread(new Runnable()
        {
            @Override
            public void run()
            {
                DialogInterface.OnClickListener dialogClickListener = new DialogInterface.OnClickListener()
                {
                    @Override
                    public void onClick(DialogInterface dialog, int which)
                    {
                        switch (which)
                        {
                            case DialogInterface.BUTTON_POSITIVE:
                                // TODO: ADD COMMAND FOR SCANNING WHOLE SELF
                                break;

                            case DialogInterface.BUTTON_NEGATIVE:
                                //No button clicked
                                break;
                        }
                    }
                };

                AlertDialog.Builder builder = new AlertDialog.Builder(context);
                builder.setMessage("Book not found, would you like to scan the whole shelf?")
                        .setPositiveButton("Yes", dialogClickListener)
                        .setNegativeButton("No", dialogClickListener)
                        .setCancelable(false)
                        .show();
            }
        });

    }


        /**
         * Called when the robot has told the app the requested book is there
         */
    private void showGetPrompt()
    {
        final Context context = this;
        runOnUiThread(new Runnable()
        {
            @Override
            public void run()
            {
                DialogInterface.OnClickListener dialogClickListener = new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which)
                        {
                            case DialogInterface.BUTTON_POSITIVE:
                                messageSender.sendCommand(new TakeBook());
                                break;

                            case DialogInterface.BUTTON_NEGATIVE:
                                //No button clicked
                                break;
                        }
                    }
                };

                AlertDialog.Builder builder = new AlertDialog.Builder(context);
                builder.setMessage("Book found, do you want to retrieve it?")
                        .setPositiveButton("Yes", dialogClickListener)
                        .setNegativeButton("No", dialogClickListener)
                        .setCancelable(false)
                        .show();
            }
        });

    }

    /**
     * Dummy function that mimics receiving the list of books from the brick
     * (will be replaced eventually)
     * @return List of books
     */
    private ArrayList<Book> getBooks()
    {
        ArrayList<Book> books = new ArrayList<>();
        books.add(new Book("9781785782343" , "Big Data How the Information Revolution Is Transforming Our Lives", "Brian Clegg", "1,1", true));
        books.add(new Book("9781447221098" , "Dirk Gently Holistic Detective Agency", "Douglas Adams", "1,2", true));
        books.add(new Book("9780241197806" , "The Castle", "Franz Kafka", "1,3", true));
        books.add(new Book("9781840226881", "Wealth of Nations", "Adam Smith", "2,1", true));
        books.add(new Book("9780349140438", "Steve Jobs", "Walter Isaacson", "2,2", true));
        books.add(new Book("9780140441185", "Thus Spoke Zarathustra", "Friedrich Nietzsche", "2,3", false));

        return books;

    }


    /**
     * Release bluetooth controller
     */
    @Override
    protected void onDestroy() {
        Log.d(TAG, "onDestroy()");
        super.onDestroy();
        if (bluetoothController.isAvailable()) {
            if (bluetoothController.getConnectionState() == State.STATE_CONNECTED) {
                bluetoothController.disconnect();
            }

            bluetoothController.release();
        }
    }

}

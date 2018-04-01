package com.luckythirteen.bibliotech.demo;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.text.Html;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.MessageParser;
import com.luckythirteen.bibliotech.brickapi.MessageSender;
import com.luckythirteen.bibliotech.brickapi.command.Command;
import com.luckythirteen.bibliotech.brickapi.command.FindBook;
import com.luckythirteen.bibliotech.brickapi.command.FullScan;
import com.luckythirteen.bibliotech.brickapi.command.QueryDB;
import com.luckythirteen.bibliotech.brickapi.command.ScanAll;
import com.luckythirteen.bibliotech.brickapi.command.ScanLower;
import com.luckythirteen.bibliotech.brickapi.command.ScanUpper;
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

public class FetchActivity extends AppCompatActivity {

    /**
     * Debugging tag
     */
    private static final String TAG = "FetchActivity";

    private ArrayList<Book> books;
    private Button btnGetBook;
    private TextView authorLabel, titleLabel, bluetoothStatus;
    private TextView titleTextView, authorTextView;
    private ImageButton reconnectButton;
    private TextView helperText;
    private ImageView helperArrow;
    private Animation arrowAnim;
    private TextView progressText;
    private ProgressBar progressBar;
    private Book chosenBook;
    private MessageSender messageSender;
    private BluetoothController bluetoothController;
    private static String targetMac;
    private final static String SHARED_PREFS_KEY = "APP_INFO";
    private final static String DEMO_ACTIVE_KEY = "demo_active";
    private boolean queriedDatabase = false;
    private boolean busy = false;          //flag for avoiding busy status
    private boolean usingInnerDB = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d(TAG, "onCreate()");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_demo_new);
        setupUI();
        setTitle("Library");

        // books = getBooks();

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
                busy = false;
                reconnectButtonVisibility = View.VISIBLE;
                resetDataAndUI();
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
                busy = false;
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
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume()");
        bluetoothController = BluetoothController.getInstance();
        bluetoothController.setBluetoothListener(bluetoothListener);

        if (bluetoothController.getConnectionState() != State.STATE_CONNECTED && bluetoothController.getConnectionState() != State.STATE_CONNECTING) {
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
        ed.apply();
    }

    private void setupUI() {
        bluetoothStatus = findViewById(R.id.txtBluetoothStatus);
        reconnectButton = findViewById(R.id.btnReconnect);

        Button btnSelectBook = findViewById(R.id.btnViewBooks);
        btnGetBook = findViewById(R.id.btnGet);
        helperArrow = findViewById(R.id.imgArrow);
        helperText = findViewById(R.id.txtSelectHelp);

        authorLabel = findViewById(R.id.txtAuthorLabel);
        titleLabel = findViewById(R.id.txtTitleLabel);
        titleTextView = findViewById(R.id.txtTitle);
        authorTextView = findViewById(R.id.txtAuthor);

        arrowAnim = AnimationUtils.loadAnimation(this.getApplicationContext(), R.anim.hover);
        helperArrow.startAnimation(arrowAnim);

        progressBar = findViewById(R.id.progressBar);
        progressText = findViewById(R.id.txtProgress);

        btnSelectBook.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onSelectBookButton();
            }
        });

        btnGetBook.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
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
    private void onSelectBookButton() {
        Log.d(TAG, "Select book button pressed");

        if(!usingInnerDB){
            if (!queriedDatabase) {
                try{
                    sendMessageWithFeedback(new QueryDB(null));
                    if (bluetoothController.getConnectionState() == State.STATE_CONNECTED) {
                        progressBar.setVisibility(View.VISIBLE);
                    }
                }catch(Exception ignored){
                }
            } else if (books != null) {
                showBookList(this.books);
            }
        }else {
            showBookList(getBooks());
        }
    }

    /**
     * Called back from the BookListArrayAdapter when the user selects a book
     *
     * @param book The book they selected
     */
    public void onBookSelected(Book book) {
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

    private void onGetButton() {
        Log.d(TAG, "onGetButton()");

        if (chosenBook != null) {
            Log.d(TAG, String.format("[FIND BOOK] \n ISBN: %s \n Title: %s \n Author: %s", chosenBook.getISBN(), chosenBook.getTitle(), chosenBook.getAuthor()));

            // Make sure MessageSender object initialised
            assert messageSender != null : "MessageSender object not initialised";

            if (books.contains(chosenBook)) {
                // Send FindBook command
                FindBook reachBook = new FindBook(chosenBook.getISBN());
                //set busy status to true, disable back button
                busy = true;

                progressBar.setVisibility(View.VISIBLE);
                progressText.setText(R.string.progressFindingBook);
                progressText.setVisibility(View.VISIBLE);

                // Send message
                sendMessageWithFeedback(reachBook);

            } else {
                final Context context = this.getApplicationContext();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(context, "Book no longer in shelf!", Toast.LENGTH_SHORT).show();
                    }
                });
            }

        } else {
            Log.e(TAG, "Get button is visible despite chosen book being NULL");
        }
    }


    /**
     * Show view containing list of books
     *
     * @param books List of books
     */
    private void showBookList(final ArrayList<Book> books) {
        this.books = books;
        final Context context = this;
        final FetchActivity fetchActivity = this;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Inflate dialog
                LayoutInflater layoutInflater = LayoutInflater.from(FetchActivity.this);
                @SuppressLint("InflateParams") View wordsPrompt = layoutInflater.inflate(R.layout.dialog_booklist, null);
                AlertDialog.Builder promptBuilder = new AlertDialog.Builder(FetchActivity.this, R.style.AlertDialogTheme);
                promptBuilder.setView(wordsPrompt);
                promptBuilder.setPositiveButton("show shelf state map", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        AlertDialog.Builder alertDialog = new AlertDialog.Builder(context);
                        alertDialog.setTitle( Html.fromHtml("<font color='#d2691e'>Choose which part of the shelf to show</font>"));
                        alertDialog.setPositiveButton("Show all",new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {

                            }
                        });
                        alertDialog.setNeutralButton("Show upper level only",new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {

                            }
                        });
                        alertDialog.setNegativeButton("Show lower level only", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {

                            }
                        });
                        alertDialog.show();
                    }
                });
                promptBuilder.setNeutralButton("cancel", null);
                promptBuilder.setNegativeButton("scan the shelf", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        AlertDialog.Builder alertDialog = new AlertDialog.Builder(context);
                        alertDialog.setTitle( Html.fromHtml("<font color='#d2691e'>Choose a way to scan the shelf</font>"));
                        alertDialog.setPositiveButton("scan all",new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                sendMessageWithFeedback(new ScanAll());
                            }
                        });
                        alertDialog.setNeutralButton("scan upper level only",new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                sendMessageWithFeedback(new ScanUpper());
                            }
                        });
                        alertDialog.setNegativeButton("scan lower level only", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                sendMessageWithFeedback(new ScanLower());
                            }
                        });
                        alertDialog.show();
                    }
                });

                final AlertDialog ad = promptBuilder.show();
                Log.w(TAG, "populateListView() - updating found words view");
                BookListArrayAdapter listAdapter = new BookListArrayAdapter(context, books, ad, fetchActivity);
                ListView listView = wordsPrompt.findViewById(R.id.lstBooks);

                // Set ListView to use updated listAdapter
                listView.setAdapter(listAdapter);
            }
        });
    }


    /**
     * Bluetooth event listener
     */
    private final BluetoothListener bluetoothListener = new BluetoothListener() {
        @Override
        public void onReadData(BluetoothDevice device, byte[] data) {
            Log.d(TAG, "Received: " + new String(data));
            String json = new String(data);
            MessageType type = MessageParser.determineMessageType(json);
            performAction(type, json);
        }

        @Override
        public void onActionStateChanged(int preState, int state) {

        }

        @Override
        public void onActionDiscoveryStateChanged(String discoveryState) {
        }

        @Override
        public void onActionScanModeChanged(int preScanMode, int scanMode) {

        }

        @Override
        public void onBluetoothServiceStateChanged(int state) {
            updateBluetoothStatusUI(state);
        }

        @Override
        public void onActionDeviceFound(BluetoothDevice device, short rssi) {

        }
    };

    /**
     * Performs an action based on the message received from the robot
     *
     * @param type Type of the message
     * @param json The raw JSON message
     */
    private void performAction(MessageType type, String json) {
        if (type == MessageType.bookList) {
            BookList books = MessageParser.getBookListFromJson(json);
            progressBar.setVisibility(View.INVISIBLE);
            progressText.setVisibility(View.INVISIBLE);

            if (books != null) {
                showBookList(books.getBooks());
                queriedDatabase = true;
            } else {
                final Context context = this.getApplicationContext();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(context, "Error parsing DB json", Toast.LENGTH_SHORT).show();
                    }
                });
            }
        } else if (type == MessageType.foundBook) {
            showGetPrompt();
        } else if (type == MessageType.missingBook) {
            showMissingBookPrompt();
        } else if (type == MessageType.busy) {
            final Context context = this.getApplicationContext();
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(context, "Robot is busy!", Toast.LENGTH_SHORT).show();
                }
            });
        }
        else if (type == MessageType.scanFinished){
            final Context context = this.getApplicationContext();
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(context, "Scan finished.", Toast.LENGTH_SHORT).show();
                }
            });
        }
        else if (type == MessageType.undefined) {
            Log.w(TAG, "Don't understand message: " + json);
        }
    }

    /**
     * Called when the robot has told the app the requested book is there
     */
    private void showMissingBookPrompt() {
        final Context context = this;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                DialogInterface.OnClickListener dialogClickListener = new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case DialogInterface.BUTTON_POSITIVE:
                                messageSender.sendCommand(new FullScan(chosenBook.getISBN()));
                                progressBar.setVisibility(View.VISIBLE);
                                progressText.setText(R.string.progressScanningShelf);
                                progressText.setVisibility(View.VISIBLE);
                                break;

                            case DialogInterface.BUTTON_NEGATIVE:
                                //No button clicked
                                break;
                        }
                    }
                };

                progressBar.setVisibility(View.INVISIBLE);
                progressText.setVisibility(View.INVISIBLE);
                busy = false;

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
    private void showGetPrompt() {
        final Context context = this;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                DialogInterface.OnClickListener dialogClickListener = new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case DialogInterface.BUTTON_POSITIVE:
                                sendMessageWithFeedback(new TakeBook(chosenBook.getISBN()));
                                removeBookFromArrayList(chosenBook);
                                break;

                            case DialogInterface.BUTTON_NEGATIVE:
                                //No button clicked
                                break;
                        }
                    }
                };

                progressBar.setVisibility(View.INVISIBLE);
                progressText.setVisibility(View.INVISIBLE);
                busy = false;

                AlertDialog.Builder builder = new AlertDialog.Builder(context);
                builder.setMessage("Book found, do you want to retrieve it?")
                        .setPositiveButton("Yes", dialogClickListener)
                        .setNegativeButton("No", dialogClickListener)
                        .setCancelable(false)
                        .show();
            }
        });
    }

    private void showScanResultPrompt(boolean found) {
        progressText.setVisibility(View.INVISIBLE);
        progressBar.setVisibility(View.INVISIBLE);
        final String message = found ? getResources().getString(R.string.scanSuccess) : getResources().getString(R.string.scanFailed);
        final Context context = this;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                AlertDialog.Builder builder = new AlertDialog.Builder(context);
                builder.setMessage(message)
                        .setNeutralButton("Ok", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int i) {
                                dialogInterface.dismiss();
                            }
                        })
                        .show();
            }
        });
    }

    /**
     * Dummy function that mimics receiving the list of books from the brick
     * (will be replaced eventually)
     *
     * @return List of books
     */
    private ArrayList<Book> getBooks() {
        ArrayList<Book> books = new ArrayList<>();
        books.add(new Book("9781785782343", "Big Data How the Information Revolution Is Transforming Our Lives", "Brian Clegg", "0", true));
        books.add(new Book("9781447221098", "Dirk Gently Holistic Detective Agency", "Douglas Adams", "1", true));
        books.add(new Book("9780241197806", "The Castle", "Franz Kafka", "2", true));
        books.add(new Book("9781840226881", "Wealth of Nations", "adam Smith", "3", true));
        books.add(new Book("9780349140438", "Steve Jobs", "Walter Isaacson", "4", true));
        books.add(new Book("9780140441185", "Thus Spoke Zarathustra", "Friedrich Nietzsche", "5", false));
        books.add(new Book("9798709872074", "Damn", "Obama", "6", false));
        books.add(new Book("3762975097525", "It's a test", "Ch Ye", "7", false));

        return books;
    }

    /**
     * Function to send a message that displays a failed message if messageSender.sendMessage()
     * returns false
     *
     * @param c Command to send
     */
    private void sendMessageWithFeedback(Command c) {
        Log.d(TAG, "sendMessageWithFeedback");
        if (messageSender == null) {
            messageSender = new MessageSender(bluetoothController);
        }

        final boolean success = messageSender.sendCommand(c);
        final Context context = this.getApplicationContext();

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (!success) {
                    if (bluetoothController.getConnectedDevice() != null)
                        Toast.makeText(context, "Failed to send message to robot :(", Toast.LENGTH_SHORT).show();
                    else
                        Toast.makeText(context, "Not connected to robot!", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void removeBookFromArrayList(Book book) {
        for (Book b : books) {
            if (b.getISBN().equals(book.getISBN())) {
                books.remove(b);
                break;
            }
        }
    }

    /**
     * Intended to be called when bluetooth connection is lost
     */
    private void resetDataAndUI() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                titleTextView.setVisibility(View.INVISIBLE);
                titleLabel.setVisibility(View.INVISIBLE);
                authorLabel.setVisibility(View.INVISIBLE);
                authorTextView.setVisibility(View.INVISIBLE);
                btnGetBook.setVisibility(View.INVISIBLE);
                helperText.setVisibility(View.VISIBLE);
                helperArrow.setVisibility(View.VISIBLE);
                helperArrow.startAnimation(arrowAnim);
                chosenBook = null;
            }
        });

    }

    /**
     * avoid robot fall into busy status
     */
    @Override
    public void onBackPressed() {
        Log.d(TAG, "onBackPressed()");
        final Context context = this.getApplicationContext();
        if (busy) {
            Toast.makeText(context, "Still trying to find the book", Toast.LENGTH_SHORT).show();
        } else {
            super.onBackPressed();
            try {
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
            } catch (Exception ignored) {
            }
        }
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

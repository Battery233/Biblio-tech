package com.luckythirteen.bibliotech.demo;

import android.content.Context;
import android.graphics.Color;
import android.support.annotation.NonNull;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import com.luckythirteen.bibliotech.R;
import com.luckythirteen.bibliotech.brickapi.obj.Book;

import java.util.List;


/**
 * Custom ArrayAdapter for displaying the found books in MapsActivity
 */

public class BookListArrayAdapter extends ArrayAdapter<Book>
{

    private static final String TAG = "BookListArrayAdapter";

    private Context context;
    private int resourceId;
    private List<Book> books;
    private AlertDialog parentDialog;
    private FetchActivity fetchActivity;

    public BookListArrayAdapter(Context context, int resourceId, List<Book> books, AlertDialog parentDialog, FetchActivity fetchActivity)
    {
        super(context, resourceId, books);

        this.context = context;
        this.resourceId = resourceId;
        this.books = books;
        this.parentDialog = parentDialog;
        this.fetchActivity = fetchActivity;
    }

    // Code adapted from: https://www.androidcode.ninja/android-viewholder-pattern-example/
    @NonNull
    @Override
    public View getView(final int position, View convertView, final ViewGroup parent)
    {
        ViewHolderItem viewHolder;


        // If we've not loaded this row before, inflate it otherwise get it's ViewHolder and update it
        if(convertView == null)
        {
            LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            convertView = inflater.inflate(R.layout.list_books_row, parent, false);


            viewHolder = new BookListArrayAdapter.ViewHolderItem();
            viewHolder.txtTitle = (TextView) convertView.findViewById(R.id.txtRowTitle);
            viewHolder.txtAuthor = (TextView)convertView.findViewById(R.id.txtRowAuthor);

            convertView.setTag(viewHolder);
        }
        else
        {
            ViewHolderItem tag = (ViewHolderItem) convertView.getTag();
            viewHolder = tag;
        }

        // Update row with info for that song
        final Book book = books.get(position);
        if(book != null)
        {

            viewHolder.txtTitle.setText(book.getTitle());
            viewHolder.txtAuthor.setText(book.getAuthor());

        }

        // Call back to fetchActivity to let it know the user has selected a book
        convertView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v)
            {
                Log.d(TAG, "Book chosen");
                fetchActivity.onBookSelected(books.get(position));

                // Close whole dialog
                parentDialog.dismiss();
            }
        });

        return convertView;
    }

    /**
     * Object representing a row
     */
    static class ViewHolderItem
    {
        TextView txtTitle, txtAuthor;
    }
}

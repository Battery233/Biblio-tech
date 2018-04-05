package com.luckythirteen.bibliotech;

import android.content.Context;
import android.support.annotation.NonNull;
import android.support.v7.app.AlertDialog;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import com.luckythirteen.bibliotech.brickapi.obj.LogEntry;

import java.util.List;


/**
 * Custom ArrayAdapter for displaying the found logs in MapsActivity
 */

class LogsArrayAdapter extends ArrayAdapter<LogEntry> {

    private static final String TAG = "BookListArrayAdapter";

    private final Context context;
    private final List<LogEntry> logs;
    private final AlertDialog parentDialog;
    private final SettingsActivity fetchActivity;

    LogsArrayAdapter(Context context, List<LogEntry> logs, AlertDialog parentDialog, SettingsActivity fetchActivity) {
        super(context, R.layout.list_logs_row, logs);

        this.context = context;
        this.logs = logs;
        this.parentDialog = parentDialog;
        this.fetchActivity = fetchActivity;
    }

    // Code adapted from: https://www.androidcode.ninja/android-viewholder-pattern-example/
    @NonNull
    @Override
    public View getView(final int position, View convertView, final ViewGroup parent) {
        ViewHolderItem viewHolder;


        // If we've not loaded this row before, inflate it otherwise get it's ViewHolder and update it
        if (convertView == null) {
            LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            try {
                convertView = inflater.inflate(R.layout.list_logs_row, parent, false);
            } catch (Exception ignored) {
            }

            viewHolder = new LogsArrayAdapter.ViewHolderItem();
            viewHolder.txtISBN = convertView.findViewById(R.id.txtRowISBN);
            viewHolder.txtTitle = convertView.findViewById(R.id.txtRowTitle);
            viewHolder.txtPos = convertView.findViewById(R.id.txtRowPos);

            convertView.setTag(viewHolder);
        } else {
            viewHolder = (ViewHolderItem) convertView.getTag();
        }

        // Update row with info for that song
        final LogEntry log = logs.get(position);
        if (log != null) {

            viewHolder.txtISBN.setText(log.getISBN());
            viewHolder.txtTitle.setText(log.getTitle());
            viewHolder.txtPos.setText(log.getPos());

        }


        return convertView;
    }

    /**
     * Object representing a row
     */
    static class ViewHolderItem {
        TextView txtISBN, txtTitle, txtPos;
    }
}

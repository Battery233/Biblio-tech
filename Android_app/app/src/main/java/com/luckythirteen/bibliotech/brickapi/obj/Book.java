package com.luckythirteen.bibliotech.brickapi.obj;

import android.os.Parcel;
import android.os.Parcelable;

public class Book implements Parcelable {
    private final String ISBN;
    private final String title;
    private final String author;
    private final String pos;
    private final boolean available;

    public Book(String ISBN, String title, String author, String pos, boolean available) {
        super();
        this.ISBN = ISBN;
        this.title = title;
        this.author = author;
        this.pos = pos;
        this.available = available;
    }

    public String getISBN() {
        return ISBN;
    }

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public String getPos() {
        return pos;
    }

    public boolean isAvailable() {
        return available;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel arg0, int arg1) {
        // TODO Auto-generated method stub
        arg0.writeString(ISBN);
        arg0.writeString(title);
        arg0.writeString(author);
        arg0.writeString(pos);
        arg0.writeByte((byte) (available ? 1 : 0));
    }

    public static final Creator CREATOR = new Creator() {

        @Override
        public Book createFromParcel(Parcel source) {
            return new Book(source.readString(), source.readString(), source.readString(), source.readString(), source.readByte() != 0);
        }

        @Override
        public Book[] newArray(int size) {
            return new Book[size];
        }
    };
}

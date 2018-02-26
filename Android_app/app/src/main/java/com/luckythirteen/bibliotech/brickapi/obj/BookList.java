package com.luckythirteen.bibliotech.brickapi.obj;


import java.util.ArrayList;

public class BookList {
    private ArrayList<Book> books;

    public BookList(ArrayList<Book> books) {
        this.books = books;
    }

    public ArrayList<Book> getBooks() {
        return books;
    }
}

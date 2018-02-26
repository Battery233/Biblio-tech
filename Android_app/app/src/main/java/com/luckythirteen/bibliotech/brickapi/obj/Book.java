package com.luckythirteen.bibliotech.brickapi.obj;


public class Book {
    private String ISBN;
    private String title;
    private String author;
    private String pos;
    private boolean available;

    public Book(String ISBN, String title, String author, String pos, boolean available) {
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
}

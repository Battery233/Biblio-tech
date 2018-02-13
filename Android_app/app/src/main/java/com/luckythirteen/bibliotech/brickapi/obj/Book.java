package com.luckythirteen.bibliotech.brickapi.obj;


public class Book
{
    private String ISBN;
    private String title;
    private String author;
    private boolean available;

    public Book(String ISBN, String title, String author, boolean available)
    {
        this.ISBN = ISBN;
        this.title = title;
        this.author = author;
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


    public boolean isAvailable() {
        return available;
    }
}

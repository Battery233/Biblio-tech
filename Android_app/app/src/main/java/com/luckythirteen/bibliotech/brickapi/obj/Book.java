package com.luckythirteen.bibliotech.brickapi.obj;


public class Book
{
    private String ISBN;
    private String title;
    private String author;

    public Book(String ISBN, String title, String author)
    {
        this.ISBN = ISBN;
        this.title = title;
        this.author = author;
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


}

package com.luckythirteen.bibliotech.brickapi.obj;

public class LogEntry
{
    private String ISBN, title, pos;

    public LogEntry(String ISBN, String title, String pos) {
        this.ISBN = ISBN;
        this.title = title;
        this.pos = pos;
    }

    public String getISBN() {
        return ISBN;
    }

    public String getTitle() {
        return title;
    }

    public String getPos() {
        return pos;
    }
}

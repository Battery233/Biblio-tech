package com.luckythirteen.bibliotech.brickapi.command;

public class TakeBook extends Command
{
    private String ISBN;

    public TakeBook(String ISBN) {
        this.ISBN = ISBN;
        this.commandType = CommandType.takeBook;
    }

    public String getISBN() {
        return ISBN;
    }
}

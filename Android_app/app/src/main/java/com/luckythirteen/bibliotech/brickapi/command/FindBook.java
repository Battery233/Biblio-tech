package com.luckythirteen.bibliotech.brickapi.command;

/**
 * Command arm to reach position of a given book
 */

public class FindBook extends Command {
    private String ISBN;

    public FindBook(String ISBN) {
        this.ISBN = ISBN;
        this.commandType = CommandType.findBook;
    }
}

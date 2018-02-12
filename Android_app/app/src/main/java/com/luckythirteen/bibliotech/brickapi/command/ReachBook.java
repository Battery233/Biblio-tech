package com.luckythirteen.bibliotech.brickapi.command;

/**
 * Command arm to reach position of a given book
 */

public class ReachBook extends Command
{
    private String ISBN;

    public ReachBook(String ISBN)
    {
        this.ISBN = ISBN;
        this.commandType = CommandType.reachBook;
    }
}

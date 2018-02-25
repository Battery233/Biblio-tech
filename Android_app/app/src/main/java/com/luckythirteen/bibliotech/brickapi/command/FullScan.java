package com.luckythirteen.bibliotech.brickapi.command;

/**
 * Command arm to reach position of a given book
 */

public class FullScan extends Command {
    private String ISBN;

    public FullScan(String ISBN) {
        this.ISBN = ISBN;
        this.commandType = CommandType.fullScan;
    }
}

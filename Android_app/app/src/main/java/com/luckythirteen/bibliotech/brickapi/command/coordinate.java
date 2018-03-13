package com.luckythirteen.bibliotech.brickapi.command;


public class coordinate extends Command {
    private String coordinate;

    public coordinate(String coordinate) {
        this.coordinate = coordinate;
        this.commandType = CommandType.coordinate;
    }
}

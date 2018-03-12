package com.luckythirteen.bibliotech.brickapi.command;

/**
 * Holds the list of commands we want to send
 */

public enum CommandType {
    undefined,
    move,
    stop,
    findBook,
    takeBook,
    queryDB,
    fullScan,
    moveDist,
    coordinate
}

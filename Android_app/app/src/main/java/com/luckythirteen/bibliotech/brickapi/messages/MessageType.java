package com.luckythirteen.bibliotech.brickapi.messages;

/**
 * Types of messages we expect to RECEIVE from the EV3
 */

public enum MessageType
{
    undefined,
    bookList,
    bookitem,
    missingBook,
    foundBook,
    malformedjson;
}

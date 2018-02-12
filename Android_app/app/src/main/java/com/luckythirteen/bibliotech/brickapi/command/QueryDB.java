package com.luckythirteen.bibliotech.brickapi.command;

import java.util.ArrayList;

public class QueryDB extends Command {
    private ArrayList<String> ISBNList;

    /**
     * @param ISBNList List of books to be searched for in the DB
     */

    public QueryDB(ArrayList<String> ISBNList) {
        this.ISBNList = ISBNList;
        this.commandType = CommandType.queryDB;
    }
}

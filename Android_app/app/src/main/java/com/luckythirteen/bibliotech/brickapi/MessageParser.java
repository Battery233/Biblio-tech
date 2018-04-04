package com.luckythirteen.bibliotech.brickapi;

import android.util.Log;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonParser;
import com.luckythirteen.bibliotech.brickapi.messages.MessageType;
import com.luckythirteen.bibliotech.brickapi.obj.Book;
import com.luckythirteen.bibliotech.brickapi.obj.BookList;

import java.util.ArrayList;

/**
 * Class to parse messages received from the EV3
 */

public class MessageParser {
    private static final String TAG = "MessageParser";

    public static MessageType determineMessageType(String json) {

        JsonParser parser = new JsonParser();

        try {
            JsonElement jsonElement = parser.parse(json);

            if (jsonElement.isJsonObject()) {
                JsonObject jsonObject = jsonElement.getAsJsonObject();
                return getType(jsonObject);
            } else {
                return MessageType.undefined;
            }
        } catch (JsonParseException e) {
            Log.w(TAG, e.getMessage());
            return MessageType.malFormedJson;
        }

    }

    private static MessageType getType(JsonObject object) {
        if (object.has(MessageType.bookList.name())) {
            return MessageType.bookList;
        } else if (object.has(MessageType.message.name())) {
            try {
                JsonObject messageObj = object.getAsJsonObject(MessageType.message.name());
                String messageContent = messageObj.get("content").getAsString();

                if (messageContent.equals(MessageType.foundBook.name())) {
                    return MessageType.foundBook;
                } else if (messageContent.equals(MessageType.missingBook.name())) {
                    return MessageType.missingBook;
                } else if (MessageType.busy.toString().equals(messageContent)) {
                    return MessageType.busy;
                } else if (MessageType.scanFinished.toString().equals(messageContent)) {
                    return MessageType.scanFinished;
                } else {
                    return MessageType.undefined;
                }
            } catch (Exception e) {
                e.printStackTrace();
                return MessageType.malFormedJson;
            }

        } else {
            return MessageType.undefined;
        }
    }

    public static BookList getBookListFromJson(String json) {
        JsonParser parser = new JsonParser();
        JsonElement jsonElement = parser.parse(json);

        ArrayList<Book> temp = new ArrayList<>();

        if (jsonElement.isJsonObject()) {
            try {
                JsonObject jsonObject = jsonElement.getAsJsonObject();
                JsonArray books = jsonObject.getAsJsonArray(MessageType.bookList.name());

                for (JsonElement e : books.getAsJsonArray()) {
                    JsonObject obj = e.getAsJsonObject();
                    temp.add(new Book(obj.get("ISBN").getAsString(), obj.get("title").getAsString(), obj.get("author").getAsString(), obj.get("pos").getAsString(), obj.get("avail").toString().equals("1")));
                }

                for (Book b : temp) {
                    System.out.println(String.format("%s\n%s\n%s\n\n", b.getTitle(), b.getAuthor(), b.getISBN()));
                }
                return new BookList(temp);
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        } else {
            // Shouldn't reach this point assuming caller determined message type beforehand
            return null;
        }
    }
}

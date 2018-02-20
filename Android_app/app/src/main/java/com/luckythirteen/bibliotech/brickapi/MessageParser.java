package com.luckythirteen.bibliotech.brickapi;

import android.util.Log;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonParser;
import com.luckythirteen.bibliotech.brickapi.messages.MessageType;

/**
 * Class to parse messages received from the EV3
 */

public class MessageParser
{
    private static final String TAG = "MessageParser";

    public static MessageType determineMessageType(String json)
    {

        JsonParser parser = new JsonParser();

        try
        {
            JsonElement jsonElement = parser.parse(json);

            if(jsonElement.isJsonObject())
            {
                JsonObject jsonObject = jsonElement.getAsJsonObject();
                return getType(jsonObject);
            }
            else
            {
                return MessageType.undefined;
            }
        }
        catch (JsonParseException e)
        {
            // Log.w(TAG, e.getMessage());
            return MessageType.undefined;
        }

    }

    private static MessageType getType(JsonObject object)
    {
        if(object.has(MessageType.booklist.name()))
        {
            return MessageType.booklist;
        }
        else
        {
            return MessageType.undefined;
        }
    }
}

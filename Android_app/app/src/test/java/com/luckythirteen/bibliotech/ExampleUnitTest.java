package com.luckythirteen.bibliotech;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonReader;
import com.luckythirteen.bibliotech.brickapi.MessageParser;
import com.luckythirteen.bibliotech.brickapi.obj.Book;

import org.junit.Test;

import java.util.ArrayList;

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * @see <a href="http://d.android.com/tools/testing">Testing documentation</a>
 */
public class ExampleUnitTest
{
    private boolean stringToBool(String s)
    {
        return s.equals("1");
    }

    @Test
    public void addition_isCorrect() throws Exception
    {
        String json = "{\n" +
                "    \"booklist\":[\n" +
                "        {\n" +
                "            \"ISBN\":\"9780241197806\",\n" +
                "            \"title\":\"The Castle\",\n" +
                "            \"author\":\"Franz Kafka\",\n" +
                "            \"avail\":0,\n" +
                "            \"pos\": \"1,2\" \n" +
                "        },\n" +
                "        {\n" +
                "            \"ISBN\":\"9781840226881\",\n" +
                "            \"title\":\"Wealth of Nations\",\n" +
                "            \"author\":\"Adam Smith\",\n" +
                "            \"avail\":1,\n" +
                "            \"pos\": \"2,3\"\n" +
                "        }\n" +
                "    ]\n" +
                "}";

        System.out.println(MessageParser.determineMessageType(json));

//        JsonParser parser = new JsonParser();
//        JsonElement jsonElement = parser.parse(json);
//
//        ArrayList<Book> temp = new ArrayList<>();
//
//        if(jsonElement.isJsonObject())
//        {
//            JsonObject jsonObject = jsonElement.getAsJsonObject();
//            if(jsonObject.has("booklist"))
//            JsonArray books = jsonObject.getAsJsonArray("booklist");
//
//            for(JsonElement e : books.getAsJsonArray())
//            {
//                JsonObject obj = e.getAsJsonObject();
//                temp.add(new Book(obj.get("ISBN").getAsString(), obj.get("title").getAsString(), obj.get("author").getAsString(), obj.get("pos").getAsString(), stringToBool(obj.get("avail").getAsString())));
//            }
//
//            for(Book b : temp)
//            {
//                System.out.println(String.format("%s\n%s\n%s\n\n", b.getTitle(), b.getAuthor(), b.getISBN()));
//            }
        }

    }

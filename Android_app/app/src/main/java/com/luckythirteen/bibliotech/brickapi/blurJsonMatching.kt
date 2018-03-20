package com.luckythirteen.bibliotech.brickapi

import android.util.Log
import org.json.JSONArray

/**
 * Created on 2018/2/27.
 * This activity is for trying to parser json when the format is not 100% correct
 * try to parse json in wrong format

"""this file is for converting the json file into the right format
the parameter input a string like this: which is the raw string we got
when the app sends the command of getting the whole list of books.
# what we got now: (by sending command to the production.db)
#[(9781785782343, 'Big Data How the Information Revolution Is Transforming Our Lives', 'Brian Clegg', '1:1', 1),
#(9781447221098, 'Dirk Gently Holistic Detective Agency', 'Douglas Adams', '1:2', 1),
#(9780241197806, 'The Castle', 'Franz Kafka', '1:3', 1),
#(9781840226881, 'Wealth of Nations', 'adam Smith', '2:1', 1),
#(9780349140438, 'Steve Jobs', 'Walter Isaacson', '2:2', 1),
#(9780140441185, 'Thus Spoke Zarathustra', 'Friedrich Nietzsche', '2:3', 0)]
"""

 * To be finished
 */

private fun parseJSONWithJSONObject(jsonData: String) {
    try {
        val jsonArray = JSONArray(jsonData)

        for (i in 0 until jsonArray.length()) {
            val jsonObject = jsonArray.getJSONObject(i)
            val pos = jsonObject.getInt("pos")
            val avail = jsonObject.getString("avail")
            val author = jsonObject.getString("author")
            val title = jsonObject.getString("title")
            val isbn = jsonObject.getString("ISBN")

            Log.d("parseJSONWithJSONObject", "pos $pos")
            Log.d("parseJSONWithJSONObject", "avail $avail")
            Log.d("parseJSONWithJSONObject", "ISBN $isbn")
            Log.d("parseJSONWithJSONObject", "author $author")
            Log.d("parseJSONWithJSONObject", "title: $title")

            val target = "{[\"pos \" $pos],[\"avail \" + $avail],[\"isbn \" + $isbn],[\"author\" + $author],[\"title\" + $title]}"
            print(target)

            val messageParser = MessageParser()
            messageParser.toString()
            //Bug here↓
            //println(messageParser.getBookListFromJson(target))
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }
}

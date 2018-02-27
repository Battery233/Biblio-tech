package com.luckythirteen.bibliotech.brickapi

import android.util.*
import org.json.JSONArray
import org.json.JSONObject

/**
 * Created on 2018/2/27.
 * This activity is for trying to parser json when the format is not 100% correct
 * try to parse json in wrong format
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

            Log.d("parseJSONWithJSONObject", "pos " + pos)
            Log.d("parseJSONWithJSONObject", "avail " + avail)
            Log.d("parseJSONWithJSONObject", "ISBN " + isbn)
            Log.d("parseJSONWithJSONObject", "author " + author)
            Log.d("parseJSONWithJSONObject", "title: " + title)

            val target = "{[\"pos \" + pos],[\"avail \" + avail],[\"isbn \" + isbn],[\"author\" + author],[\"title\" + title]}"
            print(target)

            val messageParser:MessageParser = MessageParser()
            //Bug here↓
            //println(messageParser.getBookListFromJson(target))

        }
    } catch (e: Exception) {
        e.printStackTrace()
    }
}

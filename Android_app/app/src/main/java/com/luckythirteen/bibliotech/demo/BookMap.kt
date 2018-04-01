package com.luckythirteen.bibliotech.demo

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Toast
import com.luckythirteen.bibliotech.R
import com.luckythirteen.bibliotech.brickapi.obj.Book
import java.util.ArrayList

class BookMap : AppCompatActivity() {
    // showShelf == 0, show all books
    // showShelf ==1, show books in level 1 only
    // showShelf ==2, show books in level 2 only
    var showShelf = 0
    var books = ArrayList<Book>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val intent = intent
        showShelf = intent.getIntExtra("showShelf",0)
        val bundle = getIntent().extras
        books = bundle.getParcelableArrayList<Book>("books")

        if (showShelf==0){
            setContentView(R.layout.activity_book_map_all_book)
            supportActionBar?.hide()
            Toast.makeText(this,"Show all books in shelf", Toast.LENGTH_SHORT).show()

        }else{
            setContentView(R.layout.activity_book_map_one_level)
            supportActionBar?.hide()
            Toast.makeText(this,"Show books in level $showShelf", Toast.LENGTH_SHORT).show()
        }
    }
}

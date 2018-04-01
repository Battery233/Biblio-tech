package com.luckythirteen.bibliotech.demo

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import com.luckythirteen.bibliotech.R
import com.luckythirteen.bibliotech.brickapi.obj.Book
import kotlinx.android.synthetic.main.activity_book_map_all_book.*
import java.util.*

class BookMap : AppCompatActivity() {
    // showShelf == 0, show all books
    // showShelf ==1, show books in level 1 only
    // showShelf ==2, show books in level 2 only
    var showShelf = 0
    var books = ArrayList<Book>()
    var showLevelOne = false
    var showLevelTwo = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val intent = intent
        showShelf = intent.getIntExtra("showShelf", 0)
        val bundle = getIntent().extras
        books = bundle.getParcelableArrayList<Book>("books")

        setContentView(R.layout.activity_book_map_all_book)
        supportActionBar?.hide()
        this.window.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (showShelf == 0) {
            Toast.makeText(this, "Show all books in shelf", Toast.LENGTH_SHORT).show()
            longWood.visibility = View.VISIBLE
            longWood2.visibility = View.VISIBLE
            showLevelOne = true
            showLevelTwo = true
        } else {
            Toast.makeText(this, "Show books in level $showShelf", Toast.LENGTH_SHORT).show()
            if(showShelf == 1){
                longWood.visibility = View.VISIBLE
                showLevelOne = true
            }
            if(showShelf == 2) {
                longWood2.visibility = View.VISIBLE
                showLevelTwo = true
            }
        }
        val imageId = intArrayOf(R.id.book0, R.id.book1, R.id.book2, R.id.book3,
                R.id.book4,R.id.book5, R.id.book6, R.id.book7)
        if(showLevelOne){
            // TODO: add function
        }
        if(showLevelTwo){
            // TODO: add function
        }

    }
}

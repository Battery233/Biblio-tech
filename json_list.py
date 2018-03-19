BOOKLIST = {
    "bookList":[
        {
            "ISBN":"9780241197806",
            "title":"The Castle",
            "author":"Franz Kafka",
            "avail":0,
            "pos": "1,2"
        },
        {
            "ISBN":"9781840226881",
            "title":"Wealth of Nations",
            "author":"Adam Smith",
            "avail":1,
            "pos": "2,3"
        }
    ]
}

s = '{"reachBook":{"ISBN":"9780241197806"}}'
print(s[s.index("ISBN") + 7:-3])
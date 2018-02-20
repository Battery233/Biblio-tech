# SDP-group13
[![Build Status](https://travis-ci.com/leo-mazz/sdp-group13.svg?token=JG5WwdVmCAWrpHY3Wcdp&branch=master)](https://travis-ci.com/leo-mazz/sdp-group13)

## API
The following is the interface for the communication between the app and the
EV3 brick. They exchange JSON messages over Bluetooth. The first element is the
message title (representing the command or the type of information it's being
sent) and the second is either a list of argument or the content of the message.
All arguments are optional.

```javascript
// APP TO EV3

// For testing, simple move command to engines

// Speed: int (deg / sec)
// Time: int (ms)
// Ports: "A", "B", "C", "D"
{
   "move":{
      "speed":219,
      "time":2851,
      "ports":[
         "A",
         "B",
         "C",
         "D"
      ]
   }
}

//  To be implement：
// For testing, simple stop command to engines
// Ports: "A", "B", "C", "D"
{
    "stop":{
        "ports":[
            "A",
            "B"
        ]
    }
}

//  To be implement：
// Command arm to reach position of a given book
// The default book is a random available book from the database
// ISBN: string
{
    "reachBook":{
        "ISBN":"9780241197806"
    }
}

//  To be implement：
// Command robot to take the book at its current position and bring it to the
// pick-up point
// The default book is a random available book from the database
// ISBN: string
{
    "takeBook"
}

//  To be implement：
// Retrieve list of books
// The default for ISBN is all of them
{
    "queryDB":{
        "ISBN":[
            "9780241197806",
            "9781840226881"
        ]
    }
}

// EV3 TO APP

//  To be implement：
// Send list of books
// ISBN: string
// title: string
// author: string
// avail: int (bool) Whether book is there or not
{
    "booklist":[
        {
            "ISBN":"9780241197806",
            "title":"The Castle",
            "author":"Franz Kafka",
            "avail":0
            "pos": "1,2" 
        },
        {
            "ISBN":"9781840226881",
            "title":"Wealth of Nations",
            "author":"Adam Smith",
            "avail":1
            "pos": "2,3"
        }
    ]
}

// Send message
// content: string Message to send
{
    "message":{
        "content":"Hello"
    }
}

```

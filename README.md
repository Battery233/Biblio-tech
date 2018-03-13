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
   "move": {
      "speed": 219,
      "time": 2851,
      "ports": [
         "A",
         "B",
         "C",
         "D"
      ]
   }
}

// For testing, simple stop command to engines
// Ports: "A", "B", "C", "D"
// Default is all ports
{
    "stop": {
        "ports": [
            "A",
            "B"
        ]
    }
}

// Command arm to reach position of a given book
// ISBN: string

{
    "findBook": {
        "ISBN": "9780241197806"
    }
}

// Command arm to do a full scan to look for a book
// ISBN: string

{
    "fullScan": {
        "ISBN": "9780241197806"
    }
}

// Command robot to take the book at its current position and bring it to the
// pick-up point
// ISBN: string
{
    "takeBook": {
        "ISBN": "9780241197806"
    }
}

// Retrieve list of books
// If no title is provided, fetch all the books
{
    "queryDB":{
        "title": "The castle"
    }
}

//get the positions of all motors
//return value: location(float)
//location<0 motor run backwards, >0, forwards
{
    "coordinateA":{}
    "coordinateB":{}
    "coordinateC":{}
    "coordinateD":{}
}

// EV3 TO APP

// Send list of books
// ISBN: string
// title: string
// author: string
// avail: int (bool) Whether book is there or not
{
    "booklist":[
        {
            "ISBN": "9780241197806",
            "title": "The Castle",
            "author": "Franz Kafka",
            "avail": 0,
            "pos": "1,2"
        },
        {
            "ISBN": "9781840226881",
            "title": "Wealth of Nations",
            "author": "Adam Smith",
            "avail": 1,
            "pos": "2,3"
        }
    ]
}

// Send message
// content: string, message to send (busy/missingBook/foundBook/bookNotAligned)
{
    "message": {
        "content": "busy"
    }
}

// AUXILLIARY EV3 -> MAIN EV3

// position: int (x-coordinate of robot)
{
   "position": 0
}

```

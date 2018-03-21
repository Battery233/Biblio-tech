# SDP-group13
[![Build Status](https://travis-ci.com/leo-mazz/sdp-group13.svg?token=JG5WwdVmCAWrpHY3Wcdp&branch=master)](https://travis-ci.com/leo-mazz/sdp-group13)

## API
The following is the interface for the communication between the app and the
EV3 brick. They exchange JSON messages over Bluetooth. The first element is the
message title (representing the command or the type of information it's being
sent) and the second is either a list of argument or the content of the message.
All arguments are optional.

```javascript
// APP TO RASPBERRY PI

// For testing, simple move command to engines

// Speed: int (deg / sec)
// Time: int (ms)
// Ports: { "13" / "33" : ["A", "B", "C", "D"] }

{
   "move": {
      "speed": 219,
      "time": 2851,
      "ports": {
        "13" : ["A", "B", "C", "D"]
      }
   }
}

// For testing, simple stop command to engines
// Default is all ports on all bricks
{
    "stop": {
      "ports": {
        "13" : ["A", "B", "C", "D"]
      }
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

// RASPBERRY PI TO APP

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
            "pos": "1"
        },
        {
            "ISBN": "9781840226881",
            "title": "Wealth of Nations",
            "author": "Adam Smith",
            "avail": 1,
            "pos": "2"
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

// RASPBERRY PI TO bricks

// Move robot to the left of given amount in mm
{
  "left": 10
}

// Move robot to the right of given amount in mm
{
  "right": 10
}

// Move robot up
{
  "up": {}
}

// Move robot down
{
  "down": {}
}

// BRICKS TO RASPBERRY PI
// Send message
// content: string, message to send (vertical_success, vertical_failure)
{
    "message": {
        "content": "vertical_success"
    }
}

// position: int (x-coordinate of robot)
{
   "position": 0
}



```

### MAC addresses of the devices

Raspberry Pi MAC address = "B8:27:EB:04:8B:94"

EV3-13 MAC address = "B0:B4:48:76:A2:C9"

EV3-33 MAC address = "B0:B4:48:76:E7:86"

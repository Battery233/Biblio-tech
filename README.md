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

// Time is in milliseconds. The default is 2000
// The default for ports is all of them
['move', {'speed': <speed>, 'time': 3000, 'ports':[1, 2]}]


// For testing, simple stop command to engines
// The default for ports is all of them
['stop', {'ports':[1, 2]}]


// Command arm to reach position of a given book
// The default book is a random available book from the database
['reachBook', {'ISBN': '9780241197806'}]

// Command robot to take the book at its current position and bring it to the
// pick-up point
// The default book is a random available book from the database
['takeBook', {'ISBN': '9780241197806'}]

// Retrieve list of books
// The default for ISBN is all of them
['queryDB', {'ISBN': ['9780241197806', '9781840226881']}]

// EV3 TO APP
// Send list of books
['bookList',
  [['9780241197806', 'The Castle', 'Franz Kafka', 0],
  [['9781840226881', 'Wealth of Nations', 'Adam Smith', 1]] 
]


//  To be implement： 
//  Send database to App
['databaseRequest']
```

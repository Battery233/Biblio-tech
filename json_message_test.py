import json

MESSAGE_FOUND_BOOK = 'foundBook'

message = {'message': {"content": MESSAGE_FOUND_BOOK}}
print("sending message: " + json.dumps(message))

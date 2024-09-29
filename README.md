# miz-functions
miz-functions is a Python code for Azure Functions. The code is triggered when the IoT Hub receives data, processes the data and stores it in Blob Storage.


## Usage
- Set up credential information etc. with reference to `.env.example`.
- If you want to check the detailed log, add the following code to the file and run it.
	- `logging.basicConfig(filename='./data/debug.log', level=logging.DEBUG)`
- If you want to try running locally, add the mock code to the bottom of `function_app.py` and run it.


## Code for Mock
```python
class MockEventHubEvent:
    def __init__(self, body, sequence_number):
        self._body = body
        self.sequence_number = sequence_number

    def get_body(self):
        return self._body

# Local test code
if __name__ == "__main__":
    event_data = '{ "machineID": "01", "timestamp": "00:00:00", "temperature": 25 }'
    mock_event = MockEventHubEvent(body=event_data.encode('utf-8'), sequence_number=1)
    main(mock_event)
```
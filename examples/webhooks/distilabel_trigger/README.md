<!--
This example is based on the work done by Ben on this repo https://github.com/burtenshaw/distilabel_trigger
-->


## Running the app

1. Start argilla server and argilla worker
```bash
pdm server start
pdm worker
```

2. Start the app
```bash
uvicorn webhook:server
```

## Testing the app
Annotate some record in the argilla UI and check the logs of the app to see the webhook being triggered.
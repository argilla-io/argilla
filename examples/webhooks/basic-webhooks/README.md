## Description

This is a basic webhook example to show how to setup webhook listeners  using the argilla SDK

## Running the app

1. Start argilla server and argilla worker
```bash
pdm server start
pdm worker
```

2. Start the app
```bash
uvicorn main:server
```

## Testing the app

You can see in se server logs traces when working with dataset, records and responses in the argilla server

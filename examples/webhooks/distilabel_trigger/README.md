<!--
This example is based on the work done by Ben on this repo https://github.com/burtenshaw/distilabel_trigger
-->


## Running the app

1. Start argilla server and argilla worker
```bash
pdm server start
pdm worker
```

2. Add the `localhost.org` alias in the `/etc/hosts` file to comply with the Top Level Domain URL requirement.
```
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1       localhost localhost.org
```

2. Start the app
```bash
uvicorn webhook:server
```

## Testing the app
Annotate some record in the argilla UI and check the logs of the app to see the webhook being triggered.

# Argilla Dashboard example

## Description
This is an example of a dashboard created with Argilla. The dashboard is a simple gradio app that
allows the user to see the annotation datasets progress. Users can select the dataset they want to
see and the app will display the progress of the dataset.

## Running the app

You must provide the `ARGILLA_API_URL` and `ARGILLA_API_KEY` environment variables to run the app.

```bash
ARGILLA_API_URL=<your-argilla-api> ARGILLA_API_KEY=<your-api-key> python app.py
```

## Running on HF Spaces

You can also run the app on HF Spaces. You can find the app [here](https://huggingface.co/spaces/frascuchon/argilla-progress).
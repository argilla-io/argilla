# Making the most of Markdown

This guide provides an overview of how to use Markdown and HTML in `TextFields` to format chat conversations and allow for basic multi-modal support for images, audio, video and PDFs.

The `TextField` and `TextQuestion` provide the option to enable Markdown and therefore HTML. Given the flexibility of HTML, we can get great control over the presentation of data to our annotators. We provide some out-of-the-box methods for multi-modality and chat templates in the examples below, but encourage everyone to gain inspiration to make the most of Markdown.

!!! note
    We do assume that a `TextField` or `TextQuestion` has been configured with `use_markdown=True`. Take a loot at [`Datasets`](dataset.md) to learn more about this configuration.

## Multi-modal data: images, audio, video or PDFs

### Local content through DataURLs

A DataURL is a scheme that allows data to be encoded into a base64-encoded string, and then embedded directly into HTML. To facilitate this, we offer some functions: `image_to_html`, `audio_to_html`, `video_to_thml` and `pdf_to_html`. These functions accept either the file path or the file's byte data and return the corresponding HTMurl to render the media file within the Argilla user interface. Additionally, you can also set the `width` and `height` in pixel or percentage for video and image (defaults to the original dimensions) and the autoplay and loop attributes to True for audio and video (defaults to False).

!!! warning
    DataURLs increase the memory usage of the original filesize. Additionally, different browsers enforce different size limitations for rendering DataURLs which might block the visualization experience per user.

=== "Image"

    ```python
    from argilla.markdown import image_to_html

    html = image_to_html(
        "local_image_file.png",
        width="300px",
        height="300px"
    )

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "Audio"

    ```python
    from argilla.markdown import audio_to_html

    html = audio_to_html(
        "local_audio_file.mp3",
        width="300px",
        height="300px",
        autoplay=True,
        loop=True
    )

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "Video"

    ```python
    from argilla.markdown import video_to_thml

    html = video_to_html(
        "my_video.mp4",
        width="300px",
        height="300px",
        autoplay=True,
        loop=True
    )

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "PDF"

    ```python
    from argilla.markdown import pdf_to_html

    html = pdf_to_html(
        "local_pdf.pdf",
        width="300px",
        height="300px"
    )

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

### Hosted content

Instead of uploading local files through DataURLs we can also visualize URLs that link directly to media files such as images, audio, video, and PDFs hosted on a public or private server. In this case, you can use basic HTML to visualize content that is available on something like Google Photos or decide to configure a private media server.

!!! warning
    When trying to access content from a private media server you have to ensure that the Argilla server has network access to the private media server, which might be done through something like IP whitelisting.

=== "Image"

    ```python
    html = "<img src='https://example.com/public-image-file.jpg'>"

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "Audio"

    ```python
    html = """
    <audio controls>
        <source src="https://example.com/public-audio-file.mp3" type="audio/mpeg">
    </audio>
    """"

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "Video"

    ```python
    html = """
    <video width="320" height="240" controls>
        <source src="https://example.com/public-video-file.mp4" type="video/mp4">
    </video>
    """"

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

=== "PDF"

    ```python
    html = """
    <iframe
        src="https://example.com/public-pdf-file.pdf"
        width="600"
        height="500">
    </iframe>
    """"

    rg.Record(
        fields={"markdown_enabled_field": html}
    )
    ```

## Visualize chat conversations

When working with chat data from multi-turn interaction with a Large Language Model, it might be nice to be able to visualize the conversation in a similar way as a common chat interface. To facilitate this, we offer the `chat_to_html` function, which converts messages from OpenAI chat format to a HTML-formatted chat interface.

??? Question "OpenAI chat format"
    The OpenAI chat format is a way to structure a list of messages as input from users and returns a model-generated message as output. These messages can only contain the `roles` "user" for human messages and "assistant", "system" or "model" for model-generated messages.

```python
from argilla.markdown import chat_to_html

messages = [
    {"role": "user", "content": "Hello! How are you?"},
    {"role": "assistant", "content": "I'm good, thank you! How can I assist you today?"}
]

html = chat_to_html(messages)

rg.Record(
    fields={"markdown_enabled_field": html}
)
```
# Image Support

## Feedback Datasets

You can render your images in the Argilla UI using TextField or TextQuestion. Remember to set in both cases `use_markdown` to `True`. For additional guidance, refer to the [Making Most of Markdown tutorial](/tutorials_and_integrations/tutorials/feedback/making-most-of-markdown.ipynb).

```{note}
Multimedia in Markdown is here, but it's still in the experimental phase. As we navigate the early stages, there are limits on file sizes due to ElasticSearch constraints, and the visualization and loading times may vary depending on your browser. We're on the case to improve this and welcome your feedback and suggestions!
```

## Other Datasets

You can pass a URL in the metadata field `_image_url` and the image will be rendered in the Argilla UI. You can use this in the Text Classification and the Token Classification tasks. These images need to be hosted on a publicly available URL, or private file servers like NGINX, or Minio. A good example of this would be the [tutorial by Ben Burtenshaw](/tutorials/notebooks/labelling-textclassification-sentencetransformers-semantic.ipynb).
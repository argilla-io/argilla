# Dataset

![Dataset view](../../_static/reference/webapp/dataset_view1.png)

The _Dataset_ page is the main page of the Rubrix web app.
From here you can access most of Rubrix's features, like **exploring and annotating** the records of your dataset.

The page is composed of 4 major components:

```{contents}
:local:
```

## Search bar

![Search bar](../../_static/reference/webapp/search_bar.png)

Rubrix's _search bar_ is a powerful tool that allows you to thoroughly explore your dataset, and quickly navigate through the records.
You can either fuzzy search the contents of your records, or use the more advanced [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax) of Elasticsearch to take full advantage of Rubrix's [data models](../python/python_client.rst#module-rubrix.client.models).
You can find more information about how to use the search bar in our detailed [search guide](search_records.md).

## Filters

![Dataset filters](../../_static/reference/webapp/filters_all.png)

The _filters_ provide you a quick and intuitive way to filter and sort your records with respect to various parameters.
You can find more information about how to use the filters in our detailed [filter guide](filter_records.md).

```{note}
Not all filters are available for all [tasks](../../guides/task_examples.ipynb).
```

### Predictions filter

![Predictions filter](../../_static/reference/webapp/prediction_filter.png)

This filter allows you to filter records with respect of their predictions:

- **Predicted as**: filter records by their predicted labels
- **Predicted ok**: filter records whose predictions do, or do not, match the annotations
- **Score**: filter records with respect to the score of their prediction
- **Predicted by**: filter records by the [prediction agent](../python/python_client.rst#module-rubrix.client.models)

### Annotations filter

![Annotation filters](../../_static/reference/webapp/annotation_filters.png)

This filter allows you to filter records with respect to their annotations:

- **Annotated as**: filter records with respect to their annotated labels
- **Annotated by**: filter records by the [annotation agent](../python/python_client.rst#module-rubrix.client.models)

### Status filter

![Status filters](../../_static/reference/webapp/status_filters.png)

This filter allows you to filter records with respect to their status:

- **Default**: records without any annotation or edition
- **Validated**: records with validated annotations
- **Edited**: records with annotations but still not validated

### Metadata filter

![Metadata filters](../../_static/reference/webapp/metadata_filter.png)

This filter allows you to filter records with respect to their metadata.

```{hint}
Nested metadata will be flattened and the keys will be joint by a dot.
```

### Sort records

![Sort filter](../../_static/reference/webapp/sort_filter.png)

With this component you can sort the records by various parameters, such as the predictions, annotations or their metadata.

## Record cards

The record cards are at the heart of the _Dataset_ page and contain your data.
There are three different flavors of record cards depending on the [task](../../guides/task_examples.ipynb) of your dataset.
All of them share the same basic structure showing the input text and a vertical ellipsis (or "kebab menu") on the top right that lets you access the record's metadata.
Predictions and annotations are shown depending on the current [mode](#modes) and [task](../../guides/task_examples.ipynb) of the dataset.

Check out our [exploration](explore_records.md) and [annotation](annotate_records.md) guides to see how the record cards work in the different [modes](#modes).

### Text classification

![Text classification view](../../_static/reference/webapp/text_classification.png)

In this task the predictions are given as tags below the input text.
They contain the label as well as a percentage score.
When in [Explore mode](#modes) annotations are shown as tags on the right together with a symbol indicating if the predictions match the annotations or not.
When in [Annotate mode](#modes) predictions and annotations share the same labels (annotation labels are darker).

A text classification dataset can support either single-label or multi-label classification - in other words, records are either annotated with one single label or various.

### Token classification

![Token classification view](../../_static/reference/webapp/token_classification.png)

In this task predictions and annotation are given as highlights in the input text.
Work in progress ...

### Text2Text

![Text2Text view](../../_static/reference/webapp/text2text.png)

In this task predictions and the annotation are given in a text field below the input text.
You can switch between prediction and annotation via the "_View annotation_"/"_View predictions_" buttons.
For the predictions you can find an associated score in the lower left corner.
If you have multiple predictions you can toggle between them using the arrows on the button of the record card.

## Sidebar

![Sidebar](../../_static/reference/webapp/sidebar_view.png)

The sidebar is divided into three sections.

### Modes

This section of the sidebar lets you switch between the different Rubrix modes that are covered extensively in their respective guides:

- **Explore**: this mode is for [exploring your dataset](explore_records.md) and gain valuable insights
- **Annotate**: this mode lets you conveniently [annotate your data](annotate_records.md)
- **Define rules**: this mode helps you to [define rules](define_rules.md) to automatically label your data

```{note}
Not all modes are available for all [tasks](../../guides/task_examples.ipynb).
```

### Metrics

In this section you find several "metrics" that can provide valuable insights to your dataset, or support you while annotating your records.
They are grouped into two submenus:

- **Progress**: see metrics of your annotation process, like its progress and the label distribution
- **Stats**: check the keywords of your dataset and the error distribution of the predictions

You can find more information about each metric in our dedicated [metrics guide](view_dataset_metrics.md).

### Refresh

This button allows you to refresh the list of the record cards with respect to the activated filters.
For example, if you are annotating and use the [Status filter](#status-filter) to filter out annotated records, you can press the _Refresh_ button to hide the latest annotated records.

# Examples

In this folder we will provide examples for using the API and UI.

For text classification we are looking for:

- [x] Multifield inputs
- [x] Multiclass
- [x] Large number of classes
- [ ] Multilabel
- [x] Long text input
- [x] Long text in labels
- [ ] HTML inputs


## Text classification

### Training datasets

These datasets contain labels for each record and no predictions. The use cases for this are:

- Exploration of training data to get a sense of the data, its quality, etc.
- Re-annotation: fixing potential issues in the dataset, for example wrong labels


`amazon_sentiment_es_validation_ds_multifield`: Spanish sentiment classifier with `multifield inputs` (title and body). Notebook: notebooks/text-classification/es_sentiment_amazon_hf.ipynb.

`ml_summarization_es_elpais_categories_long_text`: News dataset with long text and high number of categories. Notebook: notebooks/text-classification/es_mlsum_categorization.ipynb

### Prediction datasets

These datasets contain only predictions. The use cases for this are:

- Model monitoring: Monitoring a model in production by logging its predictions
- Feedback/training data collection: create new training data by annotating production examples.
- Custom app and dashboard development: by storing predictions into a central place build Kibana dashboards and custom apps leveraging a unified data model, search and standard agregations.

`amazon_sentiment_es_validation_ds_multifield_only_predictions`: Spanish sentiment classifier with `multifield inputs` (title and body) and predictions with a pretrained huggingface model. Notebook: (notebooks/text-classification/es_sentiment_amazon_hf.ipynb).

### Evaluation datasets (predictions + labels)

These datasets contain labels and predictions. This type of dataset can be constructed over time starting with a prediction dataset. The use cases for this are:

- Model evaluation: inspecting a model against an unseen test dataset.

- Getting production or live metrics: if starting from a prediction dataset and collecting labels from the UI, you can measure "live" or production accuracy


`amazon_sentiment_es_validation_ds_multifield_with_predictions`: Spanish sentiment classifier with `multifield inputs` (title and body) and predictions with a pretrained huggingface model. Notebook: (notebooks/text-classification/es_sentiment_amazon_hf.ipynb).

## Token classification

### Training datasets

### Prediction datasets

`explore-predictions-ner-ds_v2` Short text training dataset

### Evaluation datasets (predictions + labels)


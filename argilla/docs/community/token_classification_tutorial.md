<a href="https://colab.research.google.com/github/bikash119/argilla_autotrain/blob/main/token_classification_tutorial.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Fine-tuning a token classification model using custom Argilla Dataset and HuggingFace AutoTrain

We all would want to try out to solve some use case with a neat tool / techs available out there.
In this tutorial , I want to go over my learning journey to fine tune a model on US Patent text.

## 1. Introduction



### 1.1 Background on Named Entity Recognition (NER)

Named Entity Recognition (NER) is a fundamental task in Natural Language Processing (NLP) that involves identifying and classifying named entities in text into predefined categories such as person names, organizations, locations, medical codes, time expressions, quantities, monetary values, etc.

### 1.2 Importance of NER in Natural Language Processing

NER plays a crucial role in various NLP applications, including:
- Information Retrieval
- Question Answering Systems
- Machine Translation
- Text Summarization
- Sentiment Analysis

### 1.3 Challenges in NER for Specific Domains or Languages

While general-purpose NER models exist, they often fall short when applied to specialized domains or less-common languages due to:
- Domain-specific terminology
- Unique entity types
- Language-specific nuances

### 1.4 The Need for Custom, Fine-tuned Models

To address these challenges, fine-tuning custom NER models becomes essential. This approach allows for:
- Adaptation to specific domains: A fine-tuned model can perform better on specific tasks or domains compared to general-purpose model.
- Efficiency: Fine-tuned models often require less data and computational resources to achieve good performance on specific tasks.
- Faster inference: Smaller, task-specific models run faster than larger, general purpose ones.

### 1.5 Project Objectives and Overview

In this project, we aim to fine-tune a custom NER model for USPTO Patents. Our objectives include:
- Use [Hugging Face Spaces](https://huggingface.co/spaces) to setup an instance of [Argilla](https://argilla.io/).
- Use [Argilla](https://argilla.io/) UI to annotate our dataset with custom labels.
- Use Hugging Face [AutoTrain](https://huggingface.co/autotrain) to create a more efficient model in terms of size and inference speed.
- Demonstrating the effectiveness of transfer learning in NER tasks.


## 2. Data Background





US Patent texts are typically long, descriptive documents about inventions. The data used in this tutorial can be accessed through the [Kaggle USPTO Competition](https://www.kaggle.com/competitions/uspto-explainable-ai). Each patent contains several fields:
- Title
- Abstract
- Claims
- Description

For this tutorial, we'll focus on the `claims` field.

### 2.1 Problem Statement


  Our goal is to fine-tune a model to classify tokens in the `claims` field of a given patent.

### 2.2 Breaking Down the Problem


To achieve this goal, we need:

1. High-quality data to fine-tune a pretrained token classification model
2. Infrastructure to execute the training

## 3. Create High-Quality Data with Argilla
  [Argilla](https://github.com/argilla-io/argilla/) is an excellent tool for creating high-quality datasets with a user-friendly interface for labeling.



### 3.1 Setting Up Argilla on Hugging Face Spaces

#### 1. Visit [Hugging Face Spaces deployment page](https://huggingface.co/new-space?template=argilla/argilla-template-space)

#### 2. Create a new space:
  - Provide a name
  - Select `Docker` as Space SDK
  - Choose `Argilla` as Docker Template
  - Leave other fields empty for simplicity
  - Click on `Create Space`

#### 3. Restart the Space

Now you have an Argilla instance running on Hugging Face Spaces. Click on the space you created to go to the login screen of Argilla UI.
Access the UI using the credentials:

- Username: `admin`
- Password: `12345678` [default password]

For more options and setting up the Argilla instance for production use-cases, please refer to [Configure Argilla on Huggingface](https://docs.argilla.io/dev/getting_started/how-to-configure-argilla-on-huggingface/)

### 3.2 Create a Dataset with Argilla Python SDK

#### Step 1: Install & Import packages


```python
!pip install -U datasets argilla autotrain-advanced==0.8.8 > install_logs.txt 2>&1
```


```python
import argilla as rg
import pandas as pd
import re
import os
import random
import torch
from IPython.display import Image, display,HTML
from datasets import load_dataset, Dataset, DatasetDict,ClassLabel,Sequence,Value,Features
from transformers import pipeline,TokenClassificationPipeline
from typing import List, Dict, Union,Tuple
from google.colab import userdata
```

#### Step 2: Initialize the Argilla Client
api_url: We can get this URL by using the `https://huggingface.co/spaces/<hf_username>/<hf_space_name>?embed=true`



```python
client = rg.Argilla(
    api_url="https://bikashpatra-argilla-uspto-labelling.hf.space",
    #api_url="https://<hf_username>-<hf_space_name>.hf.space # This is url to my public space.
    api_key="admin.apikey", # default value. Shouldn't be used for production.
    # headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
#Replace `<hf-username>` and `<space-name>` with your actual Hugging Face username and space name.
```

#### Step 3: Configure the Dataset
To configure an Argilla dataset for token classification task, we will have to

1. Come up with labels specific to our problem domain: I came up with some labels by using the following prompt
 >suggest me some labels like "Process", "Product", "Composition of Matter" which can be used to annotate tokens in the claims or description section of patents filed in US

2. We need to configure fields/columns of our dataset and [`questions`](https://docs.argilla.io/latest/how_to_guides/dataset/#questions). The `questions` parameter allows you to instruct /guide the annotator on the task.In our usecase, we shall use `labels` we created for the annotators to select when annotating pieces (tokens) of text.



```python
# Labels for token classification
labels = [
    "Process", "Product", "Composition of Matter", "Method of Use",
    "Software", "Hardware", "Algorithm", "System", "Device",
    "Apparatus", "Method", "Machine", "Manufacture", "Design",
    "Pharmaceutical Formulation", "Biotechnology", "Chemical Compound",
    "Electrical Circuit"
]

# Dataset settings
settings = rg.Settings(
    guidelines="Classify individual tokens according to the specified categories, ensuring that any overlapping or nested entities are accurately captured.",
    fields=[
        rg.TextField(name="tokens", title="Text", use_markdown=True),
        rg.TextField(name="document_id", title="publication_number", use_markdown=True),
        rg.TextField(name="sentence_id", title="sentence_id", use_markdown=False)
    ],
    questions=[
        rg.SpanQuestion(
            name="span_label",
            field="tokens",
            labels=labels,
            title="Classify the tokens according to the specified categories.",
            allow_overlapping=True
        )
    ]
)
```

#### Step 4: Create dataset on Argilla instance
With the settings in places, we are ready to create our dataset using [`rg.Dataset`](https://docs.argilla.io/latest/how_to_guides/dataset/#create-a-dataset) api to create our dataset.


```python
# We name the dataset as claim_tokens
rg_dataset = rg.Dataset(
    name="claim_tokens",
    settings=settings,
)
rg_dataset.create()
```

    /usr/local/lib/python3.10/dist-packages/argilla/datasets/_resource.py:202: UserWarning: Workspace not provided. Using default workspace: admin id: fd4fc24c-fc1f-4ffe-af41-d569432d6b50
      warnings.warn(f"Workspace not provided. Using default workspace: {workspace.name} id: {workspace.id}")





    Dataset(id=UUID('a187cdad-175e-4d87-989f-a529b9999bde') inserted_at=datetime.datetime(2024, 7, 28, 7, 23, 59, 902685) updated_at=datetime.datetime(2024, 7, 28, 7, 24, 1, 901701) name='claim_tokens' status='ready' guidelines='Classify individual tokens according to the specified categories, ensuring that any overlapping or nested entities are accurately captured.' allow_extra_metadata=False workspace_id=UUID('fd4fc24c-fc1f-4ffe-af41-d569432d6b50') last_activity_at=datetime.datetime(2024, 7, 28, 7, 24, 1, 901701) url=None)



 After step 4 we should see the dataset created in Argilla UI. We can verify this by logging in to the Argilla UI `url https://huggingface.co/spaces/<hf-username>-<space-name>.hf.space)` with the default credentials.


We can look into the settings of the dataset by clicking on the settings icon next to the dataset name.



```python
def display_image(filename): display(Image(filename=filename))

display_image('/content/images/argilla_ds_list_settings.png')
```



![png](token_classification_tutorial_files/token_classification_tutorial_25_0.png)



 The Fields tab of settings screen lists down fields we configured while creating the dataset using Python SDK.


```python
display_image('/content/images/argilla_ds_settings.png')
```



![png](token_classification_tutorial_files/token_classification_tutorial_27_0.png)



#### Step 5: Insert records to the Argilla datasets

Data preparation notebook can be found [here](https://www.kaggle.com/code/boredmgr/claim-sampling)


```python
claims = pd.read_csv("/content/sample_publications.csv")
claims.head(2)
```





  <div id="df-48b0aed7-c331-4e4f-905d-c568eaa16721" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>publication_number</th>
      <th>sequence_id</th>
      <th>tokens</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>US-4444749-A</td>
      <td>0</td>
      <td>A shampoo comprising an aqueous solution of an...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>US-4444749-A</td>
      <td>1</td>
      <td>A shampoo comprising an aqueous solution of an...</td>
    </tr>
  </tbody>
</table>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-48b0aed7-c331-4e4f-905d-c568eaa16721')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-48b0aed7-c331-4e4f-905d-c568eaa16721 button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-48b0aed7-c331-4e4f-905d-c568eaa16721');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>


<div id="df-6972c075-3574-42c8-afb9-4bde476ffb34">
  <button class="colab-df-quickchart" onclick="quickchart('df-6972c075-3574-42c8-afb9-4bde476ffb34')"
            title="Suggest charts"
            style="display:none;">

<svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
     width="24px">
    <g>
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
    </g>
</svg>
  </button>

<style>
  .colab-df-quickchart {
      --bg-color: #E8F0FE;
      --fill-color: #1967D2;
      --hover-bg-color: #E2EBFA;
      --hover-fill-color: #174EA6;
      --disabled-fill-color: #AAA;
      --disabled-bg-color: #DDD;
  }

  [theme=dark] .colab-df-quickchart {
      --bg-color: #3B4455;
      --fill-color: #D2E3FC;
      --hover-bg-color: #434B5C;
      --hover-fill-color: #FFFFFF;
      --disabled-bg-color: #3B4455;
      --disabled-fill-color: #666;
  }

  .colab-df-quickchart {
    background-color: var(--bg-color);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    fill: var(--fill-color);
    height: 32px;
    padding: 0;
    width: 32px;
  }

  .colab-df-quickchart:hover {
    background-color: var(--hover-bg-color);
    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    fill: var(--button-hover-fill-color);
  }

  .colab-df-quickchart-complete:disabled,
  .colab-df-quickchart-complete:disabled:hover {
    background-color: var(--disabled-bg-color);
    fill: var(--disabled-fill-color);
    box-shadow: none;
  }

  .colab-df-spinner {
    border: 2px solid var(--fill-color);
    border-color: transparent;
    border-bottom-color: var(--fill-color);
    animation:
      spin 1s steps(1) infinite;
  }

  @keyframes spin {
    0% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
      border-left-color: var(--fill-color);
    }
    20% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    30% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
      border-right-color: var(--fill-color);
    }
    40% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    60% {
      border-color: transparent;
      border-right-color: var(--fill-color);
    }
    80% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-bottom-color: var(--fill-color);
    }
    90% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
    }
  }
</style>

  <script>
    async function quickchart(key) {
      const quickchartButtonEl =
        document.querySelector('#' + key + ' button');
      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.
      quickchartButtonEl.classList.add('colab-df-spinner');
      try {
        const charts = await google.colab.kernel.invokeFunction(
            'suggestCharts', [key], {});
      } catch (error) {
        console.error('Error during call to suggestCharts:', error);
      }
      quickchartButtonEl.classList.remove('colab-df-spinner');
      quickchartButtonEl.classList.add('colab-df-quickchart-complete');
    }
    (() => {
      let quickchartButtonEl =
        document.querySelector('#df-6972c075-3574-42c8-afb9-4bde476ffb34 button');
      quickchartButtonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';
    })();
  </script>
</div>

    </div>
  </div>




Here we are reading rows of the csv and mapping them to the fields we created during Argilla dataset configuration step.


```python
## We upload a csv with three columns : tokens, publication_number, sequence_id

publication_df = pd.read_csv("/content/sample_publications.csv")
## Convert dataframe rows to Argilla Records
records = [
    rg.Record(
        fields=
            {"tokens": "".join(row["tokens"])
            ,'document_id':str(row['publication_number'])
            ,'sentence_id':str(row['sequence_id'])
            })
  for _,row in publication_df.iterrows()
  ]
  ## Store Argilla records to Argilla Dataset
rg_dataset.records.log(records)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">DatasetRecords: The provided batch size <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">256</span> was normalized. Using value <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">149</span>.
</pre>



    Sending records...: 100%|██████████| 1/1 [00:00<00:00,  1.71batch/s]





    DatasetRecords(Dataset(id=UUID('a187cdad-175e-4d87-989f-a529b9999bde') inserted_at=datetime.datetime(2024, 7, 28, 7, 23, 59, 902685) updated_at=datetime.datetime(2024, 7, 28, 7, 24, 1, 901701) name='claim_tokens' status='ready' guidelines='Classify individual tokens according to the specified categories, ensuring that any overlapping or nested entities are accurately captured.' allow_extra_metadata=False workspace_id=UUID('fd4fc24c-fc1f-4ffe-af41-d569432d6b50') last_activity_at=datetime.datetime(2024, 7, 28, 7, 24, 1, 901701) url=None))



Once, we have records pushed to Argilla Dataset, the UI will render the records and the labels for the annotator to annotate the text.

Check the screeshots below.


```python
display_image("/content/images/annotation_screen.png")
```



![png](token_classification_tutorial_files/token_classification_tutorial_34_0.png)



#### Step 6 : Annotate tokens in every records with appropriate labels.
Login to the Argilla UI and start annotating.

Argilla UI : `https://huggingface.co/spaces/<hf-username>/<hf-space-name>`

username : `admin`

password : `12345678`



> After annotating the data , we will have to convert Argilla Dataset to HuggingFace dataset in order to use HuggingFace AutoTrain for fine-tuning the model. HF AutoTrain allows training on CSV data too which can be uploaded from AutoTrain UI. But for this tutorial we will use Huggingface dataset.



## 4. Argilla Dataset to HuggingFace Dataset

#### Step 1: Load our annotated dataset


```python
rg_dataset = client.datasets("claim_tokens")
```

#### Step 2 : Filter the rows / records which are annotated.
For us to have quick iterations on annotation and training, we should be able to annotate a few records and train our model.We can achieve it by using the [query/filter](https://docs.argilla.io/latest/how_to_guides/query/) functionality of Argilla Dataset.

Using [`rg.Query()`](https://docs.argilla.io/latest/how_to_guides/query/) api we can filter the records which are annotated for preparing our training dataset.


```python
status_filter = rg.Query(filter=rg.Filter(("response.status", "==", "submitted")))

submitted = rg_dataset.records(status_filter).to_list(flatten=True)
submitted[0]
```




    {'id': '01e9b4bb-9c98-4cec-acea-dd686cddf5f0',
     'status': 'pending',
     '_server_id': '0b6f16f3-c3dc-4947-ac77-8b65002bf350',
     'tokens': 'The FINFET of  claim 11 , wherein the conformal gate dielectric comprises a high-κ gate dielectric selected from the group consisting of: hafnium oxide (HfO 2 ), lanthanum oxide (La 2 O 3 ), and combinations thereof.',
     'document_id': 'US-11631617-B2',
     'sentence_id': '14',
     'span_label.responses': [[{'label': 'Electrical Circuit',
        'start': 4,
        'end': 10},
       {'label': 'Chemical Compound', 'start': 138, 'end': 151},
       {'label': 'Chemical Compound', 'start': 162, 'end': 177}]],
     'span_label.responses.users': ['4e9588d6-e2d6-450d-82c6-b33324d94708'],
     'span_label.responses.status': ['submitted']}



The annotated dataset cannot be fed as is to the model for fine-tuning. For token-classification task, we will have to make our data that adheres to the structure as described below.
- Dataset Structure: The dataset should typically have two main columns:
    - `tokens`: A list of words/tokens for each example.
    - `ner_tags`: A list of corresponding labels for each token. The labels must follow the [IOB labelling scheme](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)).
- Label Encoding: The labels should be integers, with each integer corresponding to a specific named entity tag.
Below functions will allow us to convert our Argilla dataset to the required dataset structure.



```python
def get_iob_tag_for_token(token_start:int, token_end:int, ner_spans:List[Dict[str, Union[int, str]]]) -> str:
    """
    Determine the IOB tag for a given token based on its position within NER spans.

    Args:
        token_start (int): The start index of the token in the text.
        token_end (int): The end index of the token in the text.
        ner_spans (List[Dict[str, Union[int, str]]]): A list of dictionaries containing NER span information.
            Each dictionary should have 'start', 'end', and 'label' keys.

    Returns:
        str: The IOB tag for the token. 'B-' prefix for the beginning of an entity,
             'I-' for inside an entity, or 'O' for outside any entity.
    """
    for span in ner_spans:
        if token_start >= span["start"] and token_end <= span["end"]:
            if token_start == span["start"]:
                return f"B-{span['label']}"
            else:
                return f"I-{span['label']}"
    return "O"


def extract_ner_tags(text:str, responses:List[Dict[str, Union[int, str]]]):
    """
    Extract NER tags for tokens in the given text based on the provided NER responses.

    Args:
        text (str): The input text to be tokenized and tagged.
        responses (List[Dict[str, Union[int, str]]]): A list of dictionaries containing NER span information.
            Each dictionary should have 'start', 'end', and 'label' keys.

    Returns:
        List[str]: A list of IOB tags corresponding to each non-whitespace token in the text.
    """
    tokens = re.split(r"(\s+)", text)
    ner_tags = []
    current_position = 0
    for token in tokens:
        if token.strip():
            token_start = current_position
            token_end = current_position + len(token)
            tag = get_iob_tag_for_token(token_start, token_end, responses)
            ner_tags.append(tag)
        current_position += len(token)
    return ner_tags
```

#### Step 3: Get tokens and theirs respective annotations


```python
def get_tokens_ner_tags(annotated_rows) -> Tuple[List[List[str]], List[List[str]]]:
    """
    Extract tokens and their corresponding NER tags from annotated rows.

    This function processes a list of annotated rows, where each row contains
    tokens and span labels. It splits the tokens and extracts NER tags for each token.

    Args:
        annotated_rows (List[Dict[str, Union[str, List[Dict[str, Union[int, str]]]]]]):
            A list of dictionaries, where each dictionary represents an annotated row.
            Each row should have a 'tokens' key (str) and a 'span_label.responses' key
            (List[Dict[str, Union[int, str]]]).

    Returns:
        Tuple[List[List[str]], List[List[str]]]: A tuple containing two elements:
            1. A list of token lists, where each inner list represents tokens for a row.
            2. A list of NER tag lists, where each inner list represents NER tags for a row.
    """
    tokens = []
    ner_tags = []
    for idx,row in enumerate(annotated_rows):
        tags = extract_ner_tags(row["tokens"], row["span_label.responses"][0])
        tks = row["tokens"].split()
        tokens.append(tks)
        ner_tags.append(tags)
    return tokens, ner_tags
train_tokens, train_ner_tags = get_tokens_ner_tags(submitted[:1])
validation_tokens, validation_ner_tags = get_tokens_ner_tags(submitted[1:2])

```

##### Vibe Check
Its always good to check our data after a few operations. This will help us understand and debug if the output of every steps results in desired output.


```python
display(HTML('''
<style>
  pre {
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  .colored-header {
    color: blue;  /* Change 'blue' to any color you prefer */
    font-size: 16px;
    margin-bottom: 8px;
}
</style>
'''))
display(HTML("<pre><span class='colored-header'>Sample Train Tokens:</span>" +
             f"{train_tokens[0]}</pre><br>"))
display(HTML("<pre><span class='colored-header'>Sample Valid Tokens:</span>" +
             f"{validation_tokens[0]}</pre><br>"))
display(HTML("<pre><span class='colored-header'>Sample Train tags:</span>" +
             f"{train_ner_tags[0]}</pre><br>"))
display(HTML("<pre><span class='colored-header'>Sample Valid tags:</span>" +
             f"{validation_ner_tags[0]}</pre>"))
```



<style>
  pre {
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  .colored-header {
    color: blue;  /* Change 'blue' to any color you prefer */
    font-size: 16px;
    margin-bottom: 8px;
}
</style>




<pre><span class='colored-header'>Sample Train Tokens:</span>['The', 'FINFET', 'of', 'claim', '11', ',', 'wherein', 'the', 'conformal', 'gate', 'dielectric', 'comprises', 'a', 'high-κ', 'gate', 'dielectric', 'selected', 'from', 'the', 'group', 'consisting', 'of:', 'hafnium', 'oxide', '(HfO', '2', '),', 'lanthanum', 'oxide', '(La', '2', 'O', '3', '),', 'and', 'combinations', 'thereof.']</pre><br>



<pre><span class='colored-header'>Sample Valid Tokens:</span>['The', 'method', 'of', 'claim', '2', ',', 'wherein', 'generating', 'the', 'one', 'or', 'more', 'possible', 'design', 'modification', 'solutions', 'based', 'at', 'least', 'in', 'part', 'on', 'the', 'set', 'of', 'attack', 'mitigation', 'rules', 'comprises', 'generating', 'the', 'one', 'or', 'more', 'possible', 'design', 'modification', 'solutions', 'by', 'inputting', 'the', 'set', 'of', 'attack', 'mitigation', 'rules', 'to', 'a', 'model', 'configured', 'to', 'perform', 'structural', 'and', 'functional', 'analysis', 'to', 'interpret', 'the', 'set', 'of', 'attack', 'mitigation', 'rules,', 'wherein', 'the', 'set', 'of', 'attack', 'mitigation', 'rules', 'comprises', 'one', 'or', 'more', 'rules', 'used', 'by', 'the', 'model', 'to', 'identify', 'the', 'key-gate', 'type', 'for', 'each', 'possible', 'design', 'modification', 'solution', 'of', 'the', 'one', 'or', 'more', 'possible', 'design', 'modification', 'solutions', 'and', 'one', 'or', 'more', 'rules', 'used', 'by', 'the', 'model', 'to', 'identify', 'the', 'location', 'where', 'to', 'insert', 'the', 'key-gate', 'type', 'for', 'each', 'possible', 'design', 'modification', 'solution', 'of', 'the', 'one', 'or', 'more', 'possible', 'design', 'modification', 'solutions.']</pre><br>



<pre><span class='colored-header'>Sample Train tags:</span>['O', 'B-Electrical Circuit', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Chemical Compound', 'I-Chemical Compound', 'O', 'O', 'O', 'B-Chemical Compound', 'I-Chemical Compound', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']</pre><br>



<pre><span class='colored-header'>Sample Valid tags:</span>['O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Process', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Process', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Algorithm', 'I-Algorithm', 'I-Algorithm', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Biotechnology', 'I-Biotechnology', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-Process', 'I-Process', 'O', 'O']</pre>


As we are trying to have our data creation and model training pipeline working, for simplicity , I have dealing with one record each for training and validation.

#### Step 4: Map labels (tags) to integers


```python
def mapped_ner_tags(ner_tags: List[List[str]]) -> List[List[int]]:
    """
    Convert a list of NER tags to their corresponding integer IDs.
    This function takes a list of lists containing string NER tags, creates a unique mapping
    of these tags to integer IDs, and then converts all tags to their respective IDs.
    Args:
        ner_tags (List[List[str]]): A list of lists, where each inner list contains string NER tags.
    Returns:
        List[List[int]]: A list of lists, where each inner list contains integer IDs
                         corresponding to the input NER tags.
    Example:
        >>> ner_tags = [['O', 'B-PER', 'I-PER'], ['O', 'B-ORG']]
        >>> mapped_ner_tags(ner_tags)
        [[0, 1, 2], [0, 3]]
    Note:
        The mapping of tags to IDs is created based on the unique tags present in the input.
        The order of ID assignment may vary between function calls if the input changes.
    """
    labels = list(set([item for sublist in ner_tags for item in sublist]))
    id2label = {i: label for i, label in enumerate(labels)}
    label2id = {label: id_ for id_, label in id2label.items()}
    mapped_ner_tags = [[label2id[label] for label in ner_tag] for ner_tag in ner_tags]
    return mapped_ner_tags
```


```python
def get_labels(ner_tags: List[List[str]]) -> List[str]:
    """
    Extract unique labels from a list of NER tag sequences.
    This function takes a list of lists containing NER tags and returns a list of unique labels
    found across all sequences.

    Args:
        ner_tags (List[List[str]]): A list of lists, where each inner list contains string NER tags.
    Returns:
        List[str]: A list of unique NER labels found in the input sequences.
    Example:
        >>> ner_tags = [['O', 'B-PER', 'I-PER'], ['O', 'B-ORG', 'I-ORG'], ['O', 'B-PER']]
        >>> get_labels(ner_tags)
        ['O', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG']
    Note:
        The order of labels in the output list is not guaranteed to be consistent
        between function calls, as it depends on the order of iteration over the set.
    """
    return list(set([item for sublist in ner_tags for item in sublist]))
```

#### Step 5: Argilla Dataset to HuggingFace Dataset
We now have our data in a structure as required for token classification dataset. We will just have to create a Hugging Face Dataset.


```python
train_labels = get_labels(train_ner_tags)
validation_labels = get_labels(validation_ner_tags)
labels = list(set(train_labels + validation_labels))
features = Features({
    "tokens": Sequence(Value("string")),
    "ner_tags": Sequence(ClassLabel(num_classes=len(labels), names=labels))
})
train_records = [
    {
        "tokens": token,
        "ner_tags": ner_tag,
    }
    for token, ner_tag in zip(train_tokens, mapped_ner_tags(train_ner_tags))
]
validation_records = [
    {
        "tokens": token,
        "ner_tags": ner_tag,
    }
    for token, ner_tag in zip(validation_tokens, mapped_ner_tags(validation_ner_tags))
]
span_dataset = DatasetDict(
    {
        "train": Dataset.from_list(train_records,features=features),
        "validation": Dataset.from_list(validation_records,features=features),
    }
)

```


```python
# assertion to verify if train split conforms the dataset structure required for fine-tuning.
assert span_dataset['train'].features['ner_tags'].feature.names is not None
```

#### Step 6: Push dataset to Hugginface Hub


```python
!huggingface-cli login
```


        _|    _|  _|    _|    _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|_|_|_|    _|_|      _|_|_|  _|_|_|_|
        _|    _|  _|    _|  _|        _|          _|    _|_|    _|  _|            _|        _|    _|  _|        _|
        _|_|_|_|  _|    _|  _|  _|_|  _|  _|_|    _|    _|  _|  _|  _|  _|_|      _|_|_|    _|_|_|_|  _|        _|_|_|
        _|    _|  _|    _|  _|    _|  _|    _|    _|    _|    _|_|  _|    _|      _|        _|    _|  _|        _|
        _|    _|    _|_|      _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|        _|    _|    _|_|_|  _|_|_|_|

        To login, `huggingface_hub` requires a token generated from https://huggingface.co/settings/tokens .
    Enter your token (input will not be visible):
    Add token as git credential? (Y/n) n
    Token is valid (permission: write).
    Your token has been saved to /root/.cache/huggingface/token
    Login successful



```python
span_dataset.push_to_hub("bikashpatra/sample_claims_annotated_hf")
```


    Uploading the dataset shards:   0%|          | 0/1 [00:00<?, ?it/s]



    Creating parquet from Arrow format:   0%|          | 0/1 [00:00<?, ?ba/s]



    Uploading the dataset shards:   0%|          | 0/1 [00:00<?, ?it/s]



    Creating parquet from Arrow format:   0%|          | 0/1 [00:00<?, ?ba/s]





    CommitInfo(commit_url='https://huggingface.co/datasets/bikashpatra/sample_claims_annotated_hf/commit/e9faaa35dda423fcb2bccde9f19cbacd832af80a', commit_message='Upload dataset', commit_description='', oid='e9faaa35dda423fcb2bccde9f19cbacd832af80a', pr_url=None, pr_revision=None, pr_num=None)



## 5. Model Fine-tuning using AutoTrain
Huggingface [AutoTrain](https://huggingface.co/autotrain) is a simple tool to train model without writing a any code. We can use autotrain to fine-tune for a range of tasks like token-classification, text-generation, Image Classification and many more. In order to use AutoTrain, we will have to first create an instance of AutoTrain in HF space. Use the [create space](https://huggingface.co/new-space?template=autotrain-projects%2Fautotrain-advanced) link. For space SDK choose Docker and select AutoTrain as Docker template. We need to choose a hardware to train our model. Check the screenshots for a quick reference



```python
display_image("/content/images/autotrain_screen1.png")
display_image("/content/images/autotrain_screen2.png")
```



![png](token_classification_tutorial_files/token_classification_tutorial_59_0.png)





![png](token_classification_tutorial_files/token_classification_tutorial_59_1.png)



### 5.1 Using AutoTrain UI

After space creation, AutoTrain UI will allow us to select from range of tasks. We will have to configure our trainer on the AutoTrain UI.
1. We will select Token classification as our task.
2. For our tutorial we will fine-tune `google-bert/bert-base-uncased`. We can choose any model from the list.
3. For DataSource select `Hugging Face Hub` which will give us a text box to fill in the dataset which we want to use for fine-tuning. We will use the dataset we pushed to Huggingface hub. I will be using the dataset that I pushed to huggingface hub `bikashpatra/claims_annotated_hf`
4. Enter the keys for `train` and `validation` split.
5. Under Column Mapping , enter the columns which store the tokens and tags. In my dataset , tokens are stored in `tokens` column and labels are stored in `ner_tags` column.
With the above 5 inputs, we can trigger `Start Training` and AutoTrain will take care of fine-tuning the base model on our dataset.


```python
display_image("/content/images/autotrain_ui.png")
```



![png](token_classification_tutorial_files/token_classification_tutorial_62_0.png)



### 5.2 Using AutoTrain CLI


```python
# for this cell to work, you will have to store HF_TOKEN as secret in colab notebook.
os.environ['TOKEN'] = userdata.get('HF_TOKEN')
```


```python
!autotrain token-classification --train \
           --username "bikashpatra" \
           --token $TOKEN \
           --backend "spaces-a10g-small" \
           --project-name "claims-token-classification" \
           --data-path "bikashpatra/sample_claims_annotated_hf" \
           --train-split "train" \
           --valid-split "validation" \
           --tokens-column "tokens" \
           --tags-column "ner_tags" \
           --model "distilbert-base-uncased" \
           --lr "2e-5" \
           --log "tensorboard" \
           --epochs "10" \
           --weight-decay "0.01" \
           --warmup-ratio "0.1" \
           --max-seq-length "256" \
           --mixed-precision "fp16" \
           --push-to-hub
```

    [1mINFO    [0m | [32m2024-08-20 06:44:18[0m | [36mautotrain.cli.run_token_classification[0m:[36mrun[0m:[36m179[0m - [1mRunning Token Classification[0m
    [33m[1mWARNING [0m | [32m2024-08-20 06:44:18[0m | [36mautotrain.trainers.common[0m:[36m__init__[0m:[36m180[0m - [33m[1mParameters supplied but not used: version, inference, config, func, train, deploy, backend[0m
    [1mINFO    [0m | [32m2024-08-20 06:44:22[0m | [36mautotrain.cli.run_token_classification[0m:[36mrun[0m:[36m185[0m - [1mJob ID: bikashpatra/autotrain-claims-token-classification[0m


AutoTrain automatically creates huggingface space for us and triggers the training job. Link to the space created is `https://huggingface.co/spaces/$JOBID where JOBID is the value that we get from the logs of autotrain cli command.


If the model training executes without any errors, our model is available with the value we provided to `--project-name`. In the above example it was `claims-token-classification`

## 6. Inference
With all the hardwork done, we have our model trained our custom dataset.We can use our trained model to predict labels for un-annotated rows.
We will use [HF Pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines) api. Pipelines are easy to use abstraction to load model and execute inference on un-seen data.In context of this tutorial _inference on un-seen text_ means predicting labels for tokens in un-annotated text.


```python
# Classify a sample text
claims_text = """
The FINFET of  claim 11 , wherein the conformal gate dielectric comprises a high-κ gate dielectric selected from
the group consisting of: hafnium oxide (HfO 2 ), lanthanum oxide (La 2 O 3 ), and combinations thereof.
"""
classifier = pipeline("token-classification", model="bikashpatra/claims-token-classification",device="cpu")
preds = classifier(claims_text)
```


```python
# The labels used for fine-tuning the model.
classifier.model.config.id2label
```




    {0: 'B-Chemical Compound',
     1: 'I-Biotechnology',
     2: 'B-Electrical Circuit',
     3: 'B-Process',
     4: 'B-Biotechnology',
     5: 'O',
     6: 'I-Chemical Compound',
     7: 'I-Process',
     8: 'B-Algorithm',
     9: 'I-Algorithm'}



## 7. Push predictions to Argilla Dataset
Using [`rg.Query`](https://docs.argilla.io/latest/how_to_guides/query/) api we filter un-annotated data and predict tokens.

The filter `rg.Filter(("response.status","==","pending"))` allows us to create a Argilla filter which we pass to [`rg.Query`](https://docs.argilla.io/latest/how_to_guides/query/) to get us all the records in Argilla dataset which has not been annotated.


```python
# Create a filter query to get only `pending` records in argilla dataset.
status_filter = rg.Query(filter=rg.Filter(("response.status", "==", "pending")))

submitted = rg_dataset.records(status_filter).to_list(flatten=True)
claims = random.sample(submitted,k=10) # pick 10 random samples.

spans = classifier(claims[0]['tokens'])
```

### 7.1 Helper function to predict the spans


```python
def predict_spanmarker(pipe:TokenClassificationPipeline,text: str):
    """
    Predict span markers for the given text using the provided pipeline.
    Args:
        pipe (TokenClassificationPipeline): A pipeline object for token classification.
        text (str): The input text for which span markers are to be predicted.
    Returns:
        List[Dict[str, Union[int, str]]]: A list of dictionaries containing the predicted span markers.
        Each dictionary should have 'start', 'end', and 'label' keys.
    """
    markers = pipe(text)
    spans = [
        {"label": marker["entity"][2:], "start": marker["start"], "end": marker["end"]}
        for marker in markers if marker["entity"] != "O"
        ]
    return spans
```


```python
updated_data=[
    {
        "span_label": predict_spanmarker(pipe=classifier, text=sample['tokens']),
        "id": sample["id"],
    }
    for sample in claims
]
```


```python
# print a few predictions
updated_data[0]['span_label'][:2]
```




    [{'label': 'Chemical Compound', 'start': 0, 'end': 3},
     {'label': 'Process', 'start': 4, 'end': 10}]



### 7.2 Insert records to Argilla Dataset.


```python
rg_dataset.records.log(records=updated_data)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">DatasetRecords: The provided batch size <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">256</span> was normalized. Using value <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">10</span>.
</pre>



    Sending records...: 100%|██████████| 1/1 [00:00<00:00,  1.15batch/s]





    DatasetRecords(Dataset(id=UUID('a187cdad-175e-4d87-989f-a529b9999bde') inserted_at=datetime.datetime(2024, 7, 28, 7, 23, 59, 902685) updated_at=datetime.datetime(2024, 7, 28, 7, 35, 55, 80617) name='claim_tokens' status='ready' guidelines='Classify individual tokens according to the specified categories, ensuring that any overlapping or nested entities are accurately captured.' allow_extra_metadata=False distribution=None workspace_id=UUID('fd4fc24c-fc1f-4ffe-af41-d569432d6b50') last_activity_at=datetime.datetime(2024, 7, 28, 7, 35, 55, 80181)))



The records we update here are stored as [`suggestions`](https://docs.argilla.io/latest/reference/argilla/records/suggestions/) and not [`responses`](https://docs.argilla.io/latest/reference/argilla/records/responses/). Responses in the context of this tutorial are created when annotator saves a annotation.Suggestions are labels predicted by model.Therefore, the records we updated here will have `response.status` as `pending` and not `submitted`. This will allow us/annotators to check the predicted labels and accept or reject model predictions.

If we want to accept model predicted annotations for tokens in a text, we may save the [`suggestions`] as [`responses`], else we will have to add / remove / edit labels applied to tokens.

## 8. Conclusion

In this comprehensive tutorial, we've explored a complete workflow for data annotation and model fine-tuning. We began by setting up an [Argilla](https://argilla.io/) instance on [Hugging Face Spaces](https://huggingface.co/spaces), providing a robust platform for data management. We then configured and created a dataset within our Argilla instance, leveraging its user-friendly interface to manually annotate a subset of records.

We continued as we exported the high-quality annotated data to a Hugging Face [dataset](https://huggingface.co/datasets), bridging the gap between annotation and model training. We then demonstrated the power of transfer learning by fine-tuning a `distilbert-base-uncased` model on this curated dataset using Hugging Face's [AutoTrain](https://huggingface.co/autotrain), a tool that simplifies the complexities of model training.

The workflow came full circle as we applied our fine-tuned model to annotate the remaining unlabeled records in the Argilla dataset, showcasing how machine learning can accelerate the annotation process. This tutorial should provide a solid foundation for implementing an iterative annotation and fine-tuning pipeline while illustrating the synergy between human expertise and machine learning capabilities.

This iterative approach allows for continuous improvement, making it an invaluable tool for tackling a wide range of natural language processing tasks efficiently and effectively.


```python

```

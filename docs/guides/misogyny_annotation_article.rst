Annotate new data to improve Misogyny Detection models using Rubrix and biome.text
==================================================================================

Hey there! In this article, I will show you how we used Rubrix to
annotate new data and use this new data to improve existing Deep
Learning models. Our use case was **Automatic Misogyny Detection**
(AMI): NLP models able to detect the underlying misogyny on a given
text. Ground-breaking work is being made every year on this subject,
with shared tasks and new ideas that push the performance of these
models closer and closer to what a moderation team of humans could do.

Alongside Rubrix, we used our amazing NLP library
`biome.text <https://github.com/recognai/biome-text>`__ to train models
with a simple workflow. Rubrix is compatible with almost any library or
service, so we were able to work back and forth with both of them.

Our objective
-------------

I was preparing my Bachelor’s thesis on the subject of Automatic
Misogyny Detection, with data from several shared tasks and competitions
on the subject. In this setting, we wanted to use the potential of
Rubrix in our favour, going beyond the classic linear workflows that are
so common in Deep Learning: gathering some data, preprocessing it,
training a model and start making inference. Rubrix breaks that scheme;
it allowed us to use a human-in-the-loop approach with retraining and
fine-tuning and to add new data in follow-up trainings.

We want to talk you more about it in this article. It is not intended to
be a tutorial, even though there will be snippets of code to reproduce
our process and get to similar result (we will simplify some aspects of
it to keep it light-weighted), but more of a story. We will focus on the
process and on what we learnt along the way.

Background
----------

The Bachelor’s thesis was focused on the Spanish language, and datasets
of misogyny in Spanish text are nothing but scarce. This was the first
hardship: finding datasets to start training some models. Luckily, there
is a very important community of shared tasks focused on the matter,
covering a lot of non-English languages. We started working with data
from `IberEval 2018 <https://sites.google.com/view/ibereval-2…>`__, a
shared-task that offered a compilation of tweets, analyzed by experts
and classified into 5 different misogyny categories and 2 targets. We
started training our first model with around three thousand instances of
annotated data.

Afterwards, the `EXIST <http://nlp.uned.es/exist2021/>`__ task at
`IberLEF 2021 <https://sites.google.com/view/iberlef2021>`__ came to our
sight. We saw there a perfect opportunity for our work on misogyny
detection, for two reasons:

-  To test our approach on misogyny detection on a different subdomain,
   with different data.
-  To expand our three-thousand-or-so instances dataset.

We covered our participation in the EXIST task in an `entry of our
blogpost <https://medium.com/recognai/against-sexism-like-a-machine-2ae9227881ef>`__.
After we submitted our runs, we shifted our efforts towards integrating
these new data into our corpus. The categorization was different:
IberEval 2018 used a categorization system of 5 categories and 2
targets, but IberLEF 2021 didn’t have a target field, and its categories
were different.

With the classic approach of Deep Learning, our journey would have ended
there: with two different, incompatible datasets. But, thanks to Rubrix,
it was only the beginning.

Merging data from different sources
-----------------------------------

The thesis started around the data corpus of IberEval 2018. Misogyny
classification, which was established by the organization, is made
following these categories: 

-   **Misogynous**: binary field, defines if the tweet is sexist or not.  
-   **Misogyny category:** denotes the type of misogynistic behaviour, if there is misogyny in the text. 5 possible categories: *Stereotype & Objectification*, *Dominance*, *Derailing*, *Sexual Harassment & Threats of Violence* and *Discredit*. 
-   **Misogyny target**: Active, if the misogyny behaviour is targetted towards a specific woman or group of women or Passive if the behaviour is targetted to many potential receivers, even women as a gender.

After our participation in EXIST at IberLEF 2021, we decied to include
more training data in the thesis. Originally, we wanted to scrap Twitter
and manually retrieve misogynistic tweets. However, using data
originally annotated from experts, which was also used by the NLP
community, seemed the right thing to do. The only problem was the label
system, which was different:

-  **Misogynous**: the same binary field as in IberEval 2018.
-  **Misogyny category**: 5 different categories; *Idelogical &
   Inequality*, *Stereotyping & Dominance*, *Objectification*, *Sexual
   Violence*, *Misogyny and Non-sexual Violence*. This labelling system
   has no misogyny target.

At this point, Rubrix became an essential tool for our work. It allowed
us to explore both data corpuses, and make an annotation phase to adapt
the data from EXIST into the standard of IberEval 2018.

Annotation as a single agent
----------------------------

Our objective was to adapt data from EXIST shared task to the standard
of IberLEF 2021. Therefore, as single annotators, we uploaded the
dataset from IberLEF 2021, and begin to explore its predictions and
annotations.

If you want to upload the training set of the EXIST task, follow the
snippet below:

.. code:: ipython3

    annotation_df = pd.read_csv('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/IberLEF%202021/Spanish/EXIST2021_test_labeled_spanish.csv')
    
    records = []
    
    for index, row in annotation_df.iterrows():
    
        item = rb.TextClassificationRecord(
            id=index,
            inputs={
                "text": row["text"]
            },
            multi_label=True,
            metadata={
                "task1_annotation": row['task1'],
                "task2_annotation": row['task2'],
            }
        )
    
        records.append(item)
    
    rb.log(records=records, name="single_annotation", tags={"project": "misogyny", "annotator": "ignacio"})

Once we’ve logged our annotation dataset into Rubrix, we can start
annotating on the UI. Let’s quickly remember how it’s done

1. Open Rubrix in your browser. If you’re running it locally, it is
   usually running on http://localhost:6900.
2. Select the ``single_annotation`` dataset.
3. On the upper-right corner, toggle the ``Annotation mode``.
4. Start selecting the categories that you think fit the input text. If
   you don’t know Spanish, don’t worry! 15 instances are not going to
   change the final model that much, and you will still learn how to
   annotate.
5. For each instance you can annotate a category by pressing it,
   discarding the record (if you think it does not fit the problem
   domain), or leave it without an annotation.

Annotating as a team
--------------------

We arranged a team of 5 different annotators, which worked over a week
to transform instances from the EXIST standard to the one from IberEval
2018. For doing so, we needed a way to merge several annotations of the
same instance into one, preserving the will of the majority, and that’s
when the Inter-Annotator Agreement (IAA) comes in handy. There are many
different types of IAAs, some based on rules and others based on
statistics.

Here’s a simplifaction of our IAA as a rule system: \* For an instance
to be annotated with a category, there must be the consensus of, at
least, two annotators. \* If there’s consensus in a sexism category, and
other annotators find there’s no sexism in the instance, it will be
discarded.

Our team of annotators was formed by Amélie, Leire, Javier, Víctor and
Ignacio. In the next cells, you can find a cell that logs the original
annotations made by our annotators (the non-annotated version is the one
downloaded in the previous section). After that, we will retrieve these
annotated datasets from Rubrix using the ``load`` command.

If you want to explore all the datasets, code and resources used in the
whole thesis, you can find them at `Temis Github
page <https://github.com/ignacioct/Temis>`__. Come to say hi!

.. code:: ipython3

    annotation_1_df = pd.read_json('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/Annotation/temis_retraining_1.json')
    annotation_2_df = pd.read_json('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/Annotation/temis_retraining_2.json')
    annotation_3_df = pd.read_json('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/Annotation/temis_retraining_3.json')
    annotation_4_df = pd.read_json('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/Annotation/temis_retraining_4.json')
    annotation_5_df = pd.read_json('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/Annotation/temis_retraining_5.json')

Now, let’s log this information into Rubrix. We are showing you how to
log one of the datasets, you just have to repeat the process and change
the names of the logged datasets, so get logged separately, and each
agent knows in which dataset she or he should annotate.

.. code:: ipython3

    records = []
    
    for index, row in annotation_1_df.iterrows():
    
        item = rb.TextClassificationRecord(
            id=index,
            inputs={
                "text": row["text"]
            },
            annotation=row["annotation"],
            annotation_agent="annotator 1",
            multi_label=True,
            metadata={
                "task1_annotation": row['task1'],
                "task2_annotation": row['task2'],
            }
        )
    
        records.append(item)
    
    rb.log(records=records, name="annotation_misogyny_1", tags={"project": "misogyny", "annotator": "annotator 1"})

One thing that should be remembered is that, for divulgation purposes,
we are simplifying the complexity of the problem. You can find more
information about how the labels in which our agents annotated are
divided into two subcategories
`here <https://github.com/ignacioct/Temis#predictions>`__.

After our logging and exploration, we can go ahead and load these
datasets from Rubrix.

.. code:: ipython3

    annotation_1 = rb.load("annotation_misogyny_1").set_index("id").sort_index()
    annotation_2 = rb.load("annotation_misogyny_2").set_index("id").sort_index()
    annotation_3 = rb.load("annotation_misogyny_3").set_index("id").sort_index()
    annotation_4 = rb.load("annotation_misogyny_4").set_index("id").sort_index()
    annotation_5 = rb.load("annotation_misogyny_5").set_index("id").sort_index()

``rb.load()`` returns a Pandas Dataframe. We will use this library to
merge our annotations into a single dataset.

.. code:: ipython3

    # We will use this tool to count ocurrences in list
    from collections import Counter
    
    annotation_final = pd.DataFrame(columns=['id','text', 'annotation', 'annotation_agent'])
    
    # Iterating through the datasets, all of them has the same length
    for i in range(len(annotation_anna)):
        
        # Extracting the annotated categories by each annotator
        category_annotated_1 = annotation_1.iloc[i]["annotation"]
        category_annotated_2 = annotation_2.iloc[i]["annotation"]
        category_annotated_3 = annotation_3.iloc[i]["annotation"]
        category_annotated_4 = annotation_4.iloc[i]["annotation"]
        category_annotated_5 = annotation_5.iloc[i]["annotation"]
        
        # Merging the annotations into a list
        annotated_categories = [category_annotated_1, category_annotated_2, category_annotated_3, category_annotated_4, category_annotated_5]
    
        # Flattening the list (if there is annotation, it is saved as an individual list)
        if not None in annotated_categories:
            annotated_categories = [item for sublist in annotated_categories for item in sublist] 
        
        # If all the elements in the list are None, we can return 'non-annotated'
        if all(annotation is None for annotation in annotated_categories):
            merged_annotation = 'non-annotated'    
        
        # Counting the annotations
        counted_annotations = Counter(annotated_categories)
        
        # Checking if the element with the most number of annotations follows the rules to be annotated
        if counted_annotations[max(counted_annotations, key=counted_annotations.get)] >= 2 and "0" not in counted_annotations:
            merged_annotation = max(counted_annotations, key=counted_annotations.get)
            
        else:
            merged_annotation = 'no-consensus'
            
            
        # As all elements in each row of the DataFrame except the annotations are the same, we can
        # retrieve information from any of the annotators. In our case is Anna.
        annotation_final = annotation_final.append({
            'id': annotation_1.iloc[i]["metadata"]["id"],
            'text': annotation_1.iloc[i]["inputs"]["text"],
            'annotation': merged_annotation,
            'annotation_agent': 'Recognai Team',
        }, ignore_index=True)

Obtained data corpus
--------------------

After our annotation session, we obtained 517 new instances, which we
added to the data corpus of the thesis. Of them, 332 were annotated as
non-sexist, and 184 as sexist.

We followed a multilabel annotation approach, so there could be more
than one misogyny category per instance. For example, in Sexual
Harassment texts, there is, usually, also some kind of dominance or
objectification, so we wanted to cover those cases. Here is our
distribution of categories.

Finally, we also categorized the target of the instance. We don’t allow
multilabel annotation here; a sexist text cannot be active and passive
at the same time.

Conclusions
-----------

Thanks to this annotation session, we were capable of including 517 new
instances into our data corpus, and therefore improve the performance of
our misogyny detection model, which was later released as a RESTful API
for app developers and users to make predictions and build moderation
pipelines around them.

Besides improving our model’s performance, we wanted to explore a
development lifecycle with Rubrix in which models can be improved over
time, with people participating as humans in the loop, analyzing the
output of our first models, searching their weaknesses and trying to
enforce them. We believe data science is an iterative process in which
monitoring obtained models and iterating through them for improvement is
key.

We invite you to test out Rubrix and join the conversation! Checkout out
our `Github page <https://github.com/recognai/rubrix>`__ and `Discussion
Forum <https://github.com/recognai/rubrix/discussions>`__ to share
ideas, questions, or just to say hi.

Appendix
--------

Here are some procedures we’ve made for this guide that were kept on the
background. If you want to reproduce all our steps, including the
training of models and some extra parts, we will give provide with cells
to do so! Feel free to change anything and try new stuff, and tell us if
you have some doubts our find something cool at our `Github
forum <https://github.com/recognai/rubrix/discussions>`__

Dependencies & Installs
~~~~~~~~~~~~~~~~~~~~~~~

During this guide, we’ve provided some minimal code for our use case.
However, to reproduce exactly our process, you will firstly need to
install Rubrix, biome.text and pandas. We will also import them.

.. code:: ipython3

    %pip install -U git+https://github.com/recognai/biome-text
    %pip install rubrix
    %pip install pandas
    exit(0)  # Force restart of the runtime

.. code:: ipython3

    from biome.text import *
    import pandas as pd
    import rubrix as rb

Training our first model
~~~~~~~~~~~~~~~~~~~~~~~~

To reproduce a simplified version of the first trained model, before
annotation, you can execute the following cells. We’ve already searched
for good-enough configurations, so you can skip that step.

Let’s start by loading the datasets

.. code:: ipython3

    # Loading the datasets
    training_ds = Dataset.from_csv('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/IberEval%202018/training_full_df.csv', index=False)
    test_ds = Dataset.from_csv('https://raw.githubusercontent.com/ignacioct/Temis/main/datasets/IberEval%202018/test_df.csv', index=False)

Creating NLP pipelines with biome.text is quick and convenient! We
performed an HPO process on the background, to find suitable
hyperparameters for this domain, so let’s use them to create our first
AMI model. Note that we’re making a pipeline with BETO, a Spanish
Transformer model, at the head. To learn more about what a Transformer
is, please visit the `Transformer guide of
biome.text <https://recognai.github.io/biome-text/v3.0.0/documentation/tutorials/4-Using_Transformers_in_biome_text.html>`__.

.. code:: ipython3

    pipeline_dict = {
        "name": "AMI_first_model",
        "features": {
            "transformers": {
                "model_name": "dccuchile/bert-base-spanish-wwm-cased", # BETO model
                "trainable": True,
                "max_length": 280,  # As we are working with data from Twitter, this is our max length
            }
        },
        "head": {
            "type": "TextClassification",
            
            # These are the possible misogyny categories.
            "labels": [
                'sexual_harassment',
                 'dominance',
                 'discredit',
                 'stereotype',
                 'derailing',
                 'non-sexist'
            ],
            "pooler": {
                "type": "lstm",
                "num_layers": 1,
                "hidden_size": 256,
                "bidirectional": True,
            },
        },
    }
    
    pl = Pipeline.from_config(pipeline_dict)

.. code:: ipython3

    trainer_config = TrainerConfiguration(
        optimizer={
            "type": "adamw",
            "lr": 0.000023636840436059507,
            "weight_decay": 0.01438297700463013,
        },
        batch_size=8,
        max_epochs=10,
    )

.. code:: ipython3

    trainer = Trainer(
        pipeline=pl,
        train_dataset=training_ds,
        valid_dataset=test_ds,
        trainer_config=trainer_config
    )

.. code:: ipython3

    trainer.fit()

After ``trainer.fit()`` stops, the results of the training and the
obtained model will be in the output folder.

We can make some predictions, and take a look at the performance of the
model.

.. code:: ipython3

    pl.predict("Las mujeres no deberían tener derecho a voto")

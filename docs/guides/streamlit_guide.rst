
Monitoring and collecting data from third-party apps
====================================================

This guide will show you **how can Rubrix be integrated into third-party applications** to collect predictions and user feedback. To do this, we are going to use `streamlit <https://streamlit.io>`_\ , an amazing tool to turn Python scripts into beautiful web-apps. 

Let's make a quick tour of the app, how you can run it locally and how to integrate Rubrix into other apps.

What does our streamlit app do?
-------------------------------

In our streamlit app we are working on a use case of *multilabel text classification*\ , 
including the inference process to make predictions and the annotations over those predictions. The NLP model is a zero-shot classifier based on `SqueezeBERT <https://huggingface.co/typeform/squeezebert-mnli>`_\ , used to predict text categories. These predictions are **mutilabel**\ , which means that more than one category can be predicted for a given text, thus the sum of the probabilities of all the candidate labels can be greater than 1. For this reasons, we let the user pick a threshold, showing which labels will be included in the prediction when changing its value. 

After the threshold is selected, the user can make its own annotation, whether or not she or he thinks the predictions are correct. This is where the *human-in-the-loop* comes into play, by responding to a model made prediction with a user made annotation, that could eventually be used to provide feedback to the model or to make retrainings.

Once the annotated labels are selected, the user can press the **log** button. A ``TextClassificationRecord`` will be created and logged into Rubrix with all the information about the process: the input text, the prediction and the annotation. This data is also displayed in the streamlit app, as the process ends. But you could always change the input text, the threshold or the annotated labels and log again!

How to run the app
------------------

We've created a `standalone repository <https://github.com/recognai/rubrix-streamlit-example>`_\  for this streamlit app, for you to clone and play around. To run the app, follow these steps:

#. Install the requirements into a fresh environment (or into your system, but take care with the dependency problems!) with Python 3, via ``pip install -r requirements.txt``.
#. Run ``streamlit run app.py``.
#. In the response prompt, streamlit will give you the localhost direction where your app will be running. You can now open it in your browser.

Rubrix integration
------------------

Rubrix can be used alongside any third-party apps via its REST API or its Python client. In our case, the logging of the record is made when the log button is pressed. In that moment, two lists will be populated:


* ``labels``\ , with the predicted labels by the zero-shot classifier
* ``selected_labels``\ , with the annotated labels, selected by the user.

Then, using the Python client we log instances of ``rubrix.TextClassificationRecord`` as follows:

.. code-block:: python

    import rubrix as rb

    item = rb.TextClassificationRecord(
                    inputs={"text": text_input},
                    prediction=labels,
                    prediction_agent="typeform/squeezebert-mnli",
                    annotation=selected_labels,
                    annotation_agent="streamlit-user",
                    multi_label=True,
                    event_timestamp=datetime.datetime.now(),
                    metadata={"model": "typeform/squeezebert-mnli"}
                )

    dataset_name = "multilabel_text_classification"

    rb.log(name=dataset_name, records=item)

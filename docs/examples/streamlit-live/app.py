import datetime
import os

import altair as alt
import pandas as pd
import streamlit as st
from transformers import pipeline

import rubrix
from rubrix.sdk.models import *


os.environ["TOKENIZERS_PARALLELISM"] = "False"  # To avoid warnings

st.set_page_config(page_title="Rubrix Demo App", layout="centered")

CANDIDATE_LABELS = [
    "business",
    "health",
    "politics",
    "sports",
    "technology",
    "entertainment",
    "computers",
    "art",
    "society",
]


def main():

    classifier = loading_model()  # Chached function, loading on top of the app

    # Header
    title, _, subtitle = st.beta_columns((2.5, 0.3, 0.7))

    title.title("How to log your ML experiments and annotations with Rubrix")

    with subtitle:
        st.write("")

    subtitle.subheader("A Web App by [Recognai](https://www.recogn.ai)")

    # First text body
    st.markdown("")  # empty space
    st.markdown(
        """Hey there, welcome! This demo will show you how to keep track of your
        live model predictions using Rubrix.
        """
    )
    st.markdown(
        """Lets make a quick experiment: an NLP model that guesses which theme a text is talking about.
        We are using a zero-shot classifier based on
        [*SqueezeBERT*](https://huggingface.co/typeform/squeezebert-mnli)"""
    )

    text_input = st.text_area(
        """For example: 'I love to watch cycling competitions!'"""
    )

    confidence_threshold = (
        0.5  # Starting value of the treshold, may be changed with the slider
    )

    if text_input:

        # Making model predictions and storing them into a dataframe
        preds = classifier(
            text_input,
            candidate_labels=CANDIDATE_LABELS,
            hypothesis_template="This text is about {}.",
            multi_class=True,
        )

        df = pd.DataFrame(
            {
                "index": preds["labels"],
                "confidence": [s for s in preds["scores"]],
                "score": [s * 100 for s in preds["scores"]],
            }
        ).set_index("index")

        # Confidence threshold slider, changes the green categories in the graph and the categories shown
        # in the multiselect so users has the classes above the threshold as preanottations
        confidence_threshold = st.slider(
            "We can select a threshold to decide which confidence must be obtained to consider it a prediction.",
            0.0,
            1.0,
            0.5,
            0.01,
        )

        # Predictions according to the threshold
        predictions = populating_predictions(df, confidence_threshold)

        df_table, _, bar_chart = st.beta_columns((1.2, 0.1, 2))

        # Class-Probabilities table
        with df_table:
            # Probabilities field
            st.dataframe(df[["score"]])

        # Class-Probabilities Chart with Confidence
        with bar_chart:
            bar_chart = bar_chart_generator(df, confidence_threshold)
            st.altair_chart(bar_chart, use_container_width=True)

        # Selection of the annotated labels
        selected_labels = st.multiselect(
            label="""With the given threshold, these are the categories predicted.
            You can change them, and your final selection will be logged as "user-validated" annotations
             (i.e., ground-truth labels).""",
            options=df.reset_index()["index"].tolist(),
            default=predictions,
        )

        st.markdown(
            """Once you are happy with the input and the categories annotated,
        press the button to log your data into Rubrix."""
        )

        log_button = center_button(
            "Log {} predictions with {} annotations".format(
                len(df["score"]), len(selected_labels)
            )
        )

        if log_button:

            # Population of labels
            labels = []
            for _, row in df.reset_index().iterrows():
                labels.append((row["index"], row["confidence"]))

            # Creation of the classification record
            item = rubrix.TextClassificationRecord(
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

            rubrix.log(name=dataset_name, records=item)

            api_url = os.getenv("RUBRIX_API_URL", "http://localhost:6900")
            # Pretty-print of the logged item
            st.markdown(
                f"""Your data has been logged! You can view your dataset in
                 [{api_url}/{dataset_name}]({api_url}/{dataset_name}),
                which has logged this object right below:"""
            )
            st.json(item.dict())

            st.markdown(
                """
            Logging this predictions into Rubrix can be done with a few commands in your Python scripts."""
            )

            # By default, Rubrix will connect to http://localhost:6900 with no security.
            st.code(
                """
            import rubrix

            item = rubrix.TextClassificationRecord(
                inputs={"text": text_input},
                prediction=labels,
                prediction_agent="typeform/squeezebert-mnli",
                annotation=selected_labels,
                annotation_agent="streamlit-user",
                multi_label=True,
                event_timestamp=datetime.datetime.now(),
                metadata={"model": "typeform/squeezebert-mnli"}
            )

            rubrix.log(name="experiment_name", records=item)

            """,
                language="python",
            )


def populating_predictions(input_df, threshold):
    """Method for getting which categories surpassed the threshold.

    Parameters
    ----------
    input_df: Pandas Dataframe
        Dataframe with predictions and score (in %)
    threshold: int
        Value from which predictions are considered valid

    Return
    ----------
    prediction_output: List[str]
        Predicted classes in descending order.
    """

    predictions_output = []
    df_sorted = input_df.sort_values(by="score")

    for index, row in df_sorted.iterrows():
        if row["score"] >= threshold * 100:
            predictions_output.append(index)

    return predictions_output


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def loading_model():
    """Loading of the zero-shot classifier. Passed to a function to include cache decorator"""

    return pipeline(
        "zero-shot-classification",
        model="typeform/squeezebert-mnli",
        framework="pt",
    )


def bar_chart_generator(df, confidence_threshold):
    """Creating the bar chart, decluttering of code from main function"""

    bars = (
        alt.Chart(df.reset_index())
        .mark_bar()
        .encode(
            x=alt.X("index", sort="-y", title=None),
            y=alt.Y("score", title=None),
            # The highlight is set based on the result
            # of the conditional statement
            color=alt.condition(
                alt.datum.score
                >= confidence_threshold
                * 100,  # If the rating is >= threshold it returns True,
                alt.value("green"),  # and the matching bars are set as green.
                # and if it does not satisfy the condition
                # the color is set to steelblue.
                alt.value("steelblue"),
            ),
        )
        .mark_bar(size=20)
    )

    return bars


def center_button(label):
    """Quickfix to center buttons, not allowed natively from Streamlit"""
    col1, col2, col3, col4, col5 = st.beta_columns((0.3, 0.3, 1, 0.3, 0.3))

    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3:
        return st.button(label)


if __name__ == "__main__":
    main()

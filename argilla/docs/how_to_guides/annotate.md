---
description: In this section, we will provide a step-by-step guide to show how to annotate records in the UI.
---
# Annotate your dataset

!!! note
    To experience the UI features firsthand, you can take a look to the [Demo ↗](https://demo.argilla.io/sign-in?auth=ZGVtbzoxMjM0NTY3OA==).

Argilla UI offers many functions to help you manage your annotation workflow, aiming to provide the most flexible approach to fit the wide variety of use cases handled by the community.

## Annotation interface overview

### Flexible layout

=== "The header"

    At the right side of the navigation breadcrumb, you can customize the dataset settings and edit your profile.

=== "The left pane"

    This area is displayed on top of **the control panel** for performing searches, applying filters and sorting results. The record card(s) are displayed one by one or in a vertical list depending on the active view: **Focus view** or **Bulk view.** A card includes one or many fields and an ellipsis menu to mainly access the record extra info like the metadata.

=== "The right pane"

    This is where you annotate your dataset. Simply fill it out as a form, then choose to Submit, Save as Draft, or Discard your response to send the records to their corresponding queues.

=== "The left bottom panel"

    This expandable area displays the annotation guidelines.

=== "The right bottom panel"

    This expandable area displays your annotation progress.

![UI overview](../assets/images/how_to_guides/annotate/ui_overview.png)

!!! tip
    The app is responsive which enable you to adapt your workspace from two to one column. You can even use your mobile to provides simple feedback on your datasets.

### Shortcuts

Argilla UI includes a range of shortcuts. For the main actions submit, discard, save as draft and the labels the keys are showed in the button.

To move from one question to another or between records using the keyboard take a look at the table below.

!!! tip
    Shortcuts provide a smoother experience, especially with a long list of labels or single-question forms.

??? "Available shortcuts"

    | Action | Keys |
    | --- | --- |
    | Activate form | ⇥ Tab |
    | Move between questions | ↓ Down arrow or ↑ Up arrow |
    | Select and unselect label | 1, 2, 3 |
    | Move between labels or ranking options | ⇥ Tab or ⇧ Shift ⇥ Tab |
    | Select rating and rank | 1, 2, 3 |
    | Fit span to character selection | Hold ⇧ Shift |
    | Activate text area | ⇧ Shift ↵ Enter |
    | Exit text area | Esc |
    | Discard | ⌫ Backspace |
    | Save draft (Mac os) | ⌘ Cmd S |
    | Save draft (Other) | Ctrl S |
    | Submit | ↵ Enter |
    | Move between pages | → Right arrow or ← Left arrow |

### View by status

The view selector is set by default on Pending.

If you are starting an annotation effort, all the records are initially kept in the Pending view. Once you annotate little by little, the records will move to the other queues: Draft, Submitted, Discarded.

- **Pending**: The records with no responses.
- **Draft**: The records with partial responses. They can be submitted or discarded later. They can’t go back to the pending queue.
- **Discarded**: The records may or may not have responses. They can be edited but can’t go back to the pending queue.
- **Submitted**: The records have been fully annotated and have already been submitted.

### Suggestions

If your dataset includes model prediction, you will see them represented by a sparkle icon `✨` in the label or value button. We call them “Suggestions”, and they appear in the form as pre-filled responses. If the suggestions convince you, you just need to click on the Submit button, and they will be considered as another annotation.

If the suggestion is incorrect, you can modify it and submit it.

The score per suggested label/value is displayed for MultiLabelQuestion and RankingQuestion.
You can also order your labels in the preference settings in order to show suggestions first, on top of the label list.

### Focus view

![Focus view](../assets/images/how_to_guides/annotate/focus_view.png)

This is the default view to annotate your dataset linearly, displaying one record after another.

**You should use this when:** getting acquainted with a dataset or when the annotation team is very diverse, the topic is generic.

Once you submit your first annotation, the next record will appear automatically. To see again your submitted record, just click on prev.

**Navigating through the records**

To navigate through the records, you can use the `Prev`, shown as `<`, and `Next`, `>` buttons on top of the record card.

Each time the page is fully refreshed, the records with modified statuses (Pending to Discarded, Pending to Save as Draft, Pending to Submitted) are sent to the corresponding queue. The **control panel** displays the **status selector**, which is set to Pending by default.

### Bulk view

![Bulk view](../assets/images/how_to_guides/annotate/bulk_view.png)

The bulk view is designed to speed up the annotation and get a quick overview of the whole dataset.

It displays the records in a vertical list. Once the view is active, some functions from the **control panel** will be available to optimize the records reading. You define the number of records to display by page between `10`, `25`, `50` , `100` and the option to fix the card height by selecting `Expand records` or `Collapse records`.

**You should use this when:** you have a good understanding of your data and want to apply your knowledge based on things like similarity search, filter patterns, and suggestion score thresholds.

**You should consider that:** bulk view does not show suggestions in bulk view (except for Spans) and will always convert questions to Draft queue when working with multiple question types.

!!! tip
    With multiple questions, think about using the bulk view to annotate massively one question. Then, you can complete the annotation per records from the draft queue.

### Annotation progress

=== "General progress view"

    On the dataset list, the global progress of the annotation task from all users is displayed. This is indicated in the `Global progress` column, which shows the number of left records to be annotated, along with a progress bar. The progress bar displays the percentage and number of records submitted, conflicting (i.e., those with overlap), discarded, and pending by hovering your mouse over it.

=== "Your own progress view"

    You can track your annotation progress in real-time. That means once you are annotating, the progress bar is incrementing in real time each time you submit or discard a record. Expanding the panel, the distribution of `Pending`, `Draft`, `Submitted` and `Discarded` responses is displayed in a donut chart.

## Discover patterns and speed up your annotation.

The UI offers various features designed to enhance your understanding of data patterns and streamline annotation tasks. Combining filters with bulk annotations can save you and your team hours of time.

**You should use this when:** you are familiar with your data and have large volumes to annotate based on verified beliefs and experience.

### Search and highlight

From the **control panel** at the top of the left pane, you can search across the entire dataset or by fields (if you have more than one in your record) and visualize matched results highlighted in color.

### Order by record semantic similarity

You can retrieve records based on their similarity to another record if vectors have been added to the dataset.

!!! note
    Consult these guides to know how to add vectors to your [dataset](dataset.md) and [records](record.md).

To initiate a semantic search, click on `Find similar` within the record you wish to use as a reference. If multiple vectors are available, select the desired vector or choose whether to retrieve the most or least similar records.

The retrieved records are then ordered by similarity, with the similarity score displayed on each record card.

While the semantic search is active, you can update the selected vector or adjust the order of similarity, and specify the number of desired results.

To cancel the search, click on the cross icon next to the reference record.

### Filter and sort by metadata, responses, and suggestions

<h4>Filter</h4>

If the dataset contains metadata, responses and suggestions, click on **Filter** in the **control panel** to display the available filters. You can select multiple filters and combine them.

!!! note
    Record info including metadata is visible from the ellipsis menu in the record card.

=== "By metadata properties"

    From the `Metadata` dropdown, type and select the property. You can set a range for integer and float properties, and select specific values for term metadata.

=== "By responses from the current user"

    From the `Responses` dropdown, type and select the question. You can set a range for rating questions and select specific values for label, multi-label, and span questions.

    !!! note
    The text and ranking questions are not available for filtering.

=== "By suggestions"

    From the Suggestions dropdown, Filter the suggestions by `Suggestion values`, `Score` , or `Agent` 

<h4>Sort</h4>

You can sort your records according to one or several attributes.

The insertion time and last update are general to all records.

The suggestion scores, response, and suggestion values for rating questions and metadata properties are available only when they were provided.

## Annotate in teams

!!! note
    Argilla 2.1 will come with automatic task distribution, which will allow you to distribute the work across several users more efficiently.

### Edit guidelines in the settings

As an `owner` or `admin`, you can edit the guidelines as much as you need from the icon settings on the header. Markdown format is enabled.

!!! tip
    If you want further guidance on good practices for guidelines during the project development, check our [blog post](https://argilla.io/blog/annotation-guidelines-practices/).
In Feedback datasets, you can also retrieve records based on their similarity with another record. To do that, make sure you have added `vector_settings` to your [dataset configuration](/practical_guides/create_update_dataset/vectors) and that your [records include vectors](/practical_guides/create_update_dataset/vectors).

In the UI, go to the record you'd like to use for the semantic search and click on `Find similar` at the top right corner of the record card. If there is more than one vector, you will be asked to select which vector to use. You can also select whether you want the most or least similar records and the number of results you would like to see.

At any time, you can expand or collapse the record that was used for the search as a reference. If you want to undo the search, just click on the cross next to the reference record.

![Snapshot of semantic search in a Feedback Dataset from Argilla's UI](/_static/images/llms/feedback_semantic_search.png)

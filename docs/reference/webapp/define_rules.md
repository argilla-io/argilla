# Define rules

_TODO: Screenshot_

The Rubrix web app has a dedicated mode to find good heuristic rules for a [weak supervision](https://www.snorkel.org/blog/weak-supervision) workflow.
As shown in our [guide](../../guides/weak-supervision.ipynb) and [tutorial](../../tutorials/weak-supervision-with-rubrix.ipynb), these rules allow you to quickly annotate your data with noisy labels in a semiautomatic way.

You can access the _Define rules_ mode via the sidebar of the [Dataset page](dataset.md).

```{note}
The _Define rules_ mode is only available for single-label text classification datasets.
```

## Query plus label

_TODO: Screenshot of the search bar and label component_

A rule in Rubrix is basically a [query](search_records.md) together with a label.
After entering a query and selecting a label, you will see the corresponding [rule metrics](#rule-metrics) on the right and the matches of your query in the record list below.

the resulton the you will see the results in the record list below. and after selecting a label
After entering a query, the list of records gets updated and shows the matches

## Rule Metrics

Check metrics + save rule

## Manage rules

Check total metrics + remove superfluous rules

## How it works

After opening a dataset, the **Define Rules** mode must be chosen on the sidebar.

If it is chosen, a **query searchbar** is displayed on the superior part of the dataset. Below, users will see the **Rules Menu** with the following features:

- **Labels**: the labels available for the dataset. More labels can be created with the `Annotation mode <annotate_records>`\_\.
- **Coverage**: the coverage obtained by the created query.
- **Annotated coverage**: the coverage obtained by the created query after annotation.
- **Correct**: the number of correct results.
- **Incorrect**: the number of incorrect results.
- **Precision**: the precision obtained by the query.

For checking the results obtained by a query, users must type on the queries searchbar and press intro when finished.

After that, **labels** will appear as editable and one of them can be chosen. Finally, results will be displayed on screen and the rule can be saved by clicking on the **Save rule** button.

Manage Rules

```
Rules can be edited by selecting them on the **Manage rules** menu, located on the right hand side of the **Rules menu**.

After clicking here, a menu with the **Overall Metrics** for the dataset and a table with the created rules will be displayed.

Here, users can search rules by name, delete or update them.
```

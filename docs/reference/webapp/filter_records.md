# Filter Records

With this component, users are able to sort the information on a dataset by using different parameters. Filters are different for each task, and they can be used in both **Annotation** and **Exploration** modes.

## How filters work

_To see a description of their components, click [here](dataset.md)._

In both modes, filters work in a very similar way:

### Filtering records in the Annotation Mode

Filtering records can be useful in big datasets, when users need to see and annotate a very specific part of the dataset.

For example, if users are annotating a dataset in a **token classification task** and they need to see how many records are annotated with one or more labels, they can use the **Annotation filter** and choose the desired combination.

<video width="100%" controls><source src="../../_static/reference/webapp/filter_records.mp4" type="video/mp4"></video>

### Filtering records in the Explore Mode

In this case, the use is basically the same, but just for analysis purposes.

Another example would be the following: if in a **text classification task** with available [**score**](../../tutorials/08-error_analysis_using_loss.ipynb), users want to sort records to see the highest or lowest loss, the **Sort filter** can be used choosing the **Score** field.

**NOTE**: There are no filters in the **Define label rules**, as this mode works with queries.

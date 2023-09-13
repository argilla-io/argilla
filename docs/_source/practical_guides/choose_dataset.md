# 🧐 Choose a dataset type

Argilla offers different datasets that are to different usecases. The main difference originates from the newer Feedback Dataset, and the older 3 older datasets for Text Classification, for Token Classification, and Text2Text. The Feedback Dataset is tailored to multi-faceted and diverse feedback and the older datasets are focused on a single NLP tasks. It is good to take note that both dataset types are actively being maintaine. On the one hand, the older datasets are more feature rich in certain points but no new features are introduced, on the other hand, the Feedback Dataset is currently less feature rich in certain points but new features will actively be added over time.

| Features                      	| FeedbackDataset 	| DatasetForTextClassification 	| DatasetForTokenClassification 	| DatasetForText2Text 	|
|-------------------------------	|-----------------	|------------------------------	|-------------------------------	|---------------------	|
| Filtering                     	| limited           | ✔️                            	| ✔️                             	| ✔️                   	|
| Sorting                       	| limited         	| ✔️                            	| ✔️                             	| ✔️                   	|
| Suggestion/predictions        	| limited       	| ✔️                            	| ✔️                             	| ✔️                   	|
| Vector search                 	|                 	| ✔️                            	| ✔️                             	| ✔️                   	|
| Weak supervision              	|                 	| ✔️                            	| ✔️                             	| ✔️                   	|
| Active learning               	|                 	| ✔️                            	| ✔️                             	| ✔️                   	|
| Text classification           	| ✔️               	| ✔️                            	|                               	|                     	|
| Token classificaiton          	|                 	|                              	| ✔️                             	|                     	|
| Text2text                     	| ✔️               	|                              	|                               	| ✔️                   	|
| Customizable tasks               	| ✔️               	|                              	|                               	|                     	|
| Multiple annotators per record 	| ✔️               	|                              	|                               	|                     	|
| Multiple-tasks in one UI      	| ✔️               	|                              	|                               	|                     	|
| Synchronization with database 	| ✔️               	|                              	|                               	|                     	|

## Feedback Dataset

### What is a Feedback Dataset?

A Feedback Dataset is a dataset that is designed to collect feedback from annotators. It is a dataset that is designed to be used in a feedback loop with a model. The feedback is collected in the form of annotations. The annotations are collected in a Feedback Task UI. The Feedback Task UI is a web application that is hosted

### Create a Feedback Dataset

###
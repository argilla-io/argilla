## 🔎 Explainability and bias

Argilla enables you to register token attributions as part of the dataset records. For getting token attributions, you can use methods such as Integrated Gradients or SHAP. These methods try to provide a mechanism to interpret model predictions. The attributions work as follows:

* **[0,1] Positive attributions (in blue)** reflect those tokens that are making the model predict the specific predicted label.

* **[-1, 0] Negative attributions (in red)** reflect those tokens that can influence the model to predict a label other than the specific predicted label.


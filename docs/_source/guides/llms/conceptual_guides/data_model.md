# Feedback Data Model
This comprehensive guide introduces the key entities in Argilla Feedback. Argilla Feedback is a powerful platform designed for collecting and managing feedback data from labelers or annotators. By understanding these entities and their relationships, you can effectively utilize the platform and leverage the collected feedback for various applications. Refer to the diagram below to visualize the relationships between the entities in Argilla Feedback.


![data-model](../../../_static/images/llms/fb-model.svg "Argilla Feedback Data Model")

## Dataset

The **Dataset** represents a collection of feedback records. It serves as the container for organizing and managing the feedback data. A dataset consists of multiple **Records**, which are individual feedback data points. Through datasets, you can configure the structure, fields, and questions for labelers to provide feedback.

## Record

A **Record** represents an individual feedback data point within a dataset. It contains the information or data that you want labelers to provide feedback on. Each record includes one or more **Fields**, which are the specific data elements or attributes that labelers will interact with during the feedback process. Fields define the structure and content of the feedback records.

## Field

A **Field** defines the schema or structure for a specific data element within a record. It represents a piece of information that labelers will see and interact with during the feedback process. Examples of fields could include text inputs, checkboxes, or dropdown menus. Fields provide the necessary context and guidance to labelers while collecting feedback.

## Question

A **Question** represents a specific query or instruction presented to labelers for feedback. Questions play a crucial role in guiding labelers and capturing their input. Argilla Feedback supports different types of questions to accommodate various feedback scenarios.

- **TextQuestion**: This type of question is suitable for collecting natural language feedback or textual responses from labelers. It allows them to provide detailed and descriptive feedback in response to the question.
- **RatingQuestion**: This type of question is designed for capturing numerical rating feedback. Labelers can rate a given aspect or attribute using a predefined scale or set of options. It is useful for obtaining quantitative feedback or evaluating specific criteria.

In addition to TextQuestions and RatingQuestions, Argilla Feedback also supports other question types such as **RankingQuestions** and **LabelSelection** questions. These question types cater to specific use cases, such as text classification tasks or ranking preferences among options.

## Response

Argilla allows for multiple concurrent annotators, seamlessly gathering feedback from many labelers. Each **Response** represents the input provided by a labeler in response to specific questions within a dataset. It includes the labeler's identification, the feedback value itself, and a status indicating whether the response has been submitted or discarded. These responses form the foundation of the collected feedback data, capturing the diverse perspectives and insights of the labelers.

## Suggestions
In upcoming releases, Argilla will introduce a powerful feature called **Suggestions**. This feature will enhance the feedback collection process by providing machine-generated feedback to labelers. Suggestions serve as automated decision-making aids, leveraging rules, models, or language models (LLMs) to accelerate the feedback process.

With Suggestions, each record can be equipped with multiple machine-generated recommendations. These suggestions can act as weak signals, seamlessly combining with human feedback to enhance the efficiency and accuracy of the feedback collection workflow. By leveraging the power of automated suggestions, labelers can make more informed decisions, resulting in a more streamlined, partially automated, and effective feedback collection process.

## Guidelines

Guidelines are a crucial component of the feedback collection process. They provide instructions, expectations, and any specific guidance for labelers to follow while providing feedback. Guidelines help ensure consistency and quality in the collected feedback. It is essential to provide clear and concise guidelines to help labelers understand the context and requirements of the feedback task.

By understanding and utilizing these entities effectively, you can configure datasets, define fields and questions, and collect high-quality feedback data. The collected feedback can be used for various purposes, such as training machine learning models, evaluating system performance, or gaining insights into user preferences.

Argilla Feedback simplifies the process of collecting and managing feedback data, empowering you to gather valuable insights and improve your models, systems, or applications based on the feedback provided by labelers.



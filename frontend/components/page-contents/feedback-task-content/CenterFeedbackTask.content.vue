<template>
  <BaseLoading v-if="$fetchState.pending" />
  <RecordFeedbackTaskAndQuestionnaireContent
    v-else-if="!$fetchState.pending"
    :datasetId="datasetId"
    :recordOffset="recordOffset"
  />
</template>

<script>
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { getTotalRecordByDatasetId } from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import {
  COMPONENT_TYPE,
  CORRESPONDING_COMPONENT_TYPE_FROM_API,
} from "@/components/feedback-task/feedbackTask.properties";

const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
});

export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 1,
      recordOffset: 0,
    };
  },
  async fetch() {
    // FETCH questions by dataset
    const { items: questions } = await this.getQuestions(this.datasetId);

    // FORMAT questions to have the shape of ORM
    const formattedQuestionsForOrm = this.factoryQuestionsForOrm(questions);

    // UPSERT formatted questions in ORM
    await upsertDatasetQuestions(formattedQuestionsForOrm);

    this.onBusEventCurrentPage();
    this.onBusEventRecordIndexToGo();
  },
  computed: {
    totalRecords() {
      return getTotalRecordByDatasetId(this.datasetId);
    },
  },
  methods: {
    onBusEventCurrentPage() {
      this.$root.$on("current-page", (currentPage) => {
        this.currentPage = currentPage;
        this.recordOffset = currentPage - 1;
      });
    },
    onBusEventRecordIndexToGo() {
      this.$root.$on("go-to-record-index", (recordIndexToGo) => {
        if (recordIndexToGo >= 0) {
          // NOTE - recordIndex start at 0 / page start at 1
          const pageToGo = recordIndexToGo + 1;

          if (this.currentPage < this.totalRecords) {
            this.recordOffset = recordIndexToGo;
            this.currentPage = pageToGo;
            this.$root.$emit("current-page", this.currentPage);
          }
          if (recordIndexToGo < this.totalRecords) {
            this.updatePageQueryParam(pageToGo);
          }
        }
      });
    },
    updatePageQueryParam(page) {
      this.$router.push({
        path: this.$route.path,
        query: { _page: page },
      });
    },
    factoryQuestionsForOrm(initialQuestions) {
      return initialQuestions.map(
        (
          {
            id: questionId,
            name: questionName,
            title: questionTitle,
            required: isRequired,
            settings: questionSettings,
          },
          index
        ) => {
          const componentTypeFromBack = questionSettings.type.toLowerCase();
          const componentType =
            CORRESPONDING_COMPONENT_TYPE_FROM_API[componentTypeFromBack];

          const formattedOptions = this.formatOptionsFromQuestionApi(
            questionSettings.options,
            questionName,
            componentType
          );
          return {
            id: questionId,
            name: questionName,
            dataset_id: this.datasetId,
            order: index,
            question: questionTitle,
            options: formattedOptions,
            is_required: isRequired,
            component_type: componentType,
            placeholder: questionSettings?.placeholder ?? null,
            tooltip_message: questionSettings?.tooltip ?? null,
          };
        }
      );
    },
    formatOptionsFromQuestionApi(options, questionName, componentType) {
      // NOTE - the value of the options in questions from API and the value in the DatasetQuestion ORM are different
      // - the value from the options from the questions in API could be anything (string, number, etc.)
      // - the value from the options in the DatasetQuestion ORM is a boolean, it the state of the 'checkbox  true (if selected) or false (not selected)
      // => this is why value is initiate as false for RATING and "" for FREE_TEXT

      let defaultValueByComponent = null;
      switch (componentType.toUpperCase()) {
        case COMPONENT_TYPE.FREE_TEXT:
          defaultValueByComponent = "";
          break;
        case COMPONENT_TYPE.RATING:
          defaultValueByComponent = false;
          break;
        case COMPONENT_TYPE.SINGLE_LABEL:
          defaultValueByComponent = false;
          break;
        default:
          console.log(`the component type ${componentType} is unknown`);
      }

      if (options) {
        return options?.map((option) => {
          const optionText = option.text ?? option.value;
          const paramObject = {
            value: defaultValueByComponent,
            text: optionText,
            prefixId: questionName,
            suffixId: option.value,
          };

          return this.factoryOption(paramObject);
        });
      }

      return [
        this.factoryOption({
          value: "",
          prefixId: questionName,
        }),
      ];
    },
    factoryOption({ value = null, text = "", prefixId, suffixId }) {
      return {
        id: `${prefixId}${suffixId ? `_${suffixId}` : ""}`,
        value,
        text,
      };
    },
    async getQuestions(datasetId) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/questions`
        );

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_QUESTIONS,
        };
      }
    },
  },
  destroyed() {
    this.$root.$off("current-page");
    this.$root.$off("go-to-record-index");
  },
};
</script>

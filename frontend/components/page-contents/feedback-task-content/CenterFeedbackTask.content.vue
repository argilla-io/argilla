<template>
  <BaseLoading v-if="$fetchState.pending" />
  <RecordFeedbackTaskAndQuestionnaireContent
    :key="rerenderChildren"
    v-else-if="!$fetchState.pending"
    :datasetId="datasetId"
    :recordOffset="recordOffset"
    :recordStatusToFilterWith="recordStatusFilteringValue"
  />
</template>

<script>
import { Notification } from "@/models/Notifications";
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { upsertDatasetFields } from "@/models/feedback-task-model/dataset-field/datasetField.queries";
import { getTotalRecordByDatasetId } from "@/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import {
  RECORD_STATUS,
  deleteAllRecords,
  getRecordStatusByDatasetIdAndRecordIndex,
} from "@/models/feedback-task-model/record/record.queries";
import {
  COMPONENT_TYPE,
  CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API,
  CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API,
} from "@/components/feedback-task/feedbackTask.properties";
import { FEEDBACK_TASK_PROPERTIES } from "@/components/feedback-task/feedbackTask.properties";
const TYPE_OF_FEEDBACK = Object.freeze({
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
  ERROR_FETCHING_FIELDS: "ERROR_FETCHING_FIELDS",
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
      rerenderChildren: 0,
      areResponsesUntouched: true,
    };
  },
  async fetch() {
    // FETCH questions AND fields by dataset
    const { items: questions } = await this.getQuestions(this.datasetId);
    const { items: fields } = await this.getFields(this.datasetId);

    // FORMAT questions AND fields to have the shape of ORM
    const formattedQuestionsForOrm = this.factoryQuestionsForOrm(questions);
    const formattedFieldsForOrm = this.factoryFieldsForOrm(fields);

    // UPSERT formatted questions in ORM
    await upsertDatasetQuestions(formattedQuestionsForOrm);
    await upsertDatasetFields(formattedFieldsForOrm);

    this.onBusEventCurrentPage();
    this.onBusEventRecordIndexToGo();
    this.onBusEventAreResponsesUntouched();
  },
  computed: {
    totalRecords() {
      return getTotalRecordByDatasetId(this.datasetId);
    },
    recordStatusFilteringValue() {
      const { _status: recordStatus } = this.$route.query;
      return recordStatus ?? RECORD_STATUS.PENDING.toLowerCase();
    },
    recordStatus() {
      return getRecordStatusByDatasetIdAndRecordIndex(
        this.datasetId,
        this.recordOffset
      );
    },
  },
  watch: {
    totalRecords(newTotalRecord) {
      if (!newTotalRecord) this.areResponsesUntouched = true;
    },
    async recordStatusFilteringValue(newStatus, oldStatus) {
      // NOTE 1 - each time the filter change, clean records orm && rerender the children component
      !this.areResponsesUntouched ||
        (await this.goToFirstPageAndRerenderChildren());

      // NOTE 2 - if responses are untouched, toast is not shown. Else, toast is shown
      this.checkIfAreResponsesUntouchedAndRouteStatusIsDifferent(newStatus) ||
        this.showNotificationBeforeChangeStatus({
          eventToFireOnClick: async () =>
            this.goToFirstPageAndRerenderChildren(),
          eventToFireOnClose: () =>
            this.stayOnCurrentPageAndReplaceStatusByOldStatus(oldStatus),
          message: this.toastMessage,
          buttonMessage: this.buttonMessage,
          typeOfToast: this.typeOfToast,
        });
    },
  },
  created() {
    this.toastMessage = "Your changes will be lost if you move to another view";
    this.buttonMessage = FEEDBACK_TASK_PROPERTIES.CONTINUE;
    this.typeOfToast = "warning";
  },
  methods: {
    showNotificationBeforeChangeStatus({
      eventToFireOnClick,
      eventToFireOnClose,
      message,
      buttonMessage,
      typeOfToast,
    }) {
      Notification.dispatch("notify", {
        message: message ?? "",
        numberOfChars: 20000,
        type: typeOfToast ?? "warning",
        buttonText: buttonMessage ?? "",
        async onClick() {
          eventToFireOnClick();
        },
        async onClose() {
          eventToFireOnClose();
        },
      });
    },
    stayOnCurrentPageAndReplaceStatusByOldStatus(oldStatus) {
      // TODO - go to previous status if user click on close button
      this.updatePageQueryParam("_status", oldStatus);
    },
    async goToFirstPageAndRerenderChildren() {
      await deleteAllRecords();
      // Go to first page on change filter
      this.$root.$emit("current-page", 1);
      this.rerenderChildren++;
    },
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
            this.updatePageQueryParam("_page", pageToGo);
          }
        }
      });
    },
    onBusEventAreResponsesUntouched() {
      this.$root.$on("are-responses-untouched", (areResponsesUntouched) => {
        this.areResponsesUntouched = areResponsesUntouched;
      });
    },
    updatePageQueryParam(param, value) {
      this.$router.push({
        path: this.$route.path,
        query: { ...this.$route.query, [param]: value },
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
            description: questionDescription,
          },
          index
        ) => {
          const componentTypeFromBack = questionSettings.type.toLowerCase();
          const componentType =
            CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API[
              componentTypeFromBack
            ];

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
            description: questionDescription ?? null,
          };
        }
      );
    },
    factoryFieldsForOrm(initialFields) {
      return initialFields.map(
        (
          {
            id: fieldId,
            name: fieldName,
            title: fieldTitle,
            required: isRequired,
            settings: fieldSettings,
          },
          index
        ) => {
          const componentTypeFromBack =
            fieldSettings?.type?.toLowerCase() ?? null;

          const componentType = componentTypeFromBack
            ? CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API[componentTypeFromBack]
            : null;

          return {
            id: fieldId,
            name: fieldName,
            dataset_id: this.datasetId,
            order: index,
            title: fieldTitle,
            is_required: isRequired,
            component_type: componentType,
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
    checkIfAreResponsesUntouchedAndRouteStatusIsDifferent(status) {
      return (
        this.areResponsesUntouched ||
        this.recordStatus?.toLowerCase() === status
      );
    },
    async getFields(datasetId) {
      try {
        const { data } = await this.$axios.get(
          `/v1/datasets/${datasetId}/fields`
        );

        return data;
      } catch (err) {
        throw {
          response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FIELDS,
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

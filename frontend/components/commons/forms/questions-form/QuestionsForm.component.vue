<template>
  <form
    :key="renderForm"
    class="questions-form"
    :class="{ '--edited-form': !isFormUntouched }"
    @submit.prevent="onSubmit"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <p class="questions-form__title --body1 --medium">
          Submit your feedback
        </p>
        <p class="questions-form__guidelines-link">
          Read the
          <NuxtLink
            :to="{
              name: 'dataset-id-settings',
              params: { id: datasetId },
            }"
            target="_blank"
            >annotation guidelines <svgicon name="external-link" width="12"
          /></NuxtLink>
        </p>
      </div>
      <div class="form-group" v-for="input in inputs" :key="input.id">
        <TextAreaComponent
          v-if="input.component_type === COMPONENT_TYPE.FREE_TEXT"
          :title="input.question"
          :optionId="`${input.name}_0`"
          :placeholder="input.placeholder"
          :value="input.options[0].text"
          :useMarkdown="input.use_markdown"
          :isRequired="input.is_required"
          :tooltipMessage="input.description"
          @on-change-value="
            onChangeTextArea({ newOptions: $event, idComponent: input.id })
          "
          @on-error="onError"
        />

        <SingleLabelComponent
          v-if="input.component_type === COMPONENT_TYPE.SINGLE_LABEL"
          :title="input.question"
          :options="input.options"
          :isRequired="input.is_required"
          :tooltipMessage="input.description"
          @on-change-single-label="
            onChangeMonoSelection({ newOptions: $event, idComponent: input.id })
          "
          @on-error="onError"
        />

        <RatingComponent
          v-if="input.component_type === COMPONENT_TYPE.RATING"
          :title="input.question"
          v-model="input.options"
          :isRequired="input.is_required"
          :tooltipMessage="input.description"
          @on-error="onError"
        />
      </div>
    </div>
    <div class="footer-form">
      <div class="footer-form__left-footer">
        <BaseButton
          type="button"
          ref="clearButton"
          class="primary text"
          @click.prevent="onClear"
        >
          <span v-text="'Clear'" />
        </BaseButton>
      </div>
      <div class="footer-form__right-area">
        <BaseButton
          type="button"
          ref="discardButton"
          class="primary outline"
          @on-click="onDiscard"
          :disabled="isRecordDiscarded"
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          ref="submitButton"
          type="submit"
          name="submitButton"
          value="submitButton"
          class="primary"
          :disabled="disableSubmitButton"
        >
          <span v-text="'Submit'" />
        </BaseButton>
      </div>
    </div>
  </form>
</template>

<script>
import { isEqual, cloneDeep } from "lodash";
import { Notification } from "@/models/Notifications";
import { COMPONENT_TYPE } from "@/components/feedback-task/feedbackTask.properties";
import {
  getOptionsOfQuestionByDatasetIdAndQuestionName,
  getComponentTypeOfQuestionByDatasetIdAndQuestionName,
} from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import {
  getRecordIndexByRecordId,
  updateRecordStatusByRecordId,
  RECORD_STATUS,
  RESPONSE_STATUS_FOR_API,
} from "@/models/feedback-task-model/record/record.queries";
import {
  getRecordResponsesIdByRecordId,
  upsertRecordResponses,
  deleteRecordResponsesByUserIdAndResponseId,
} from "@/models/feedback-task-model/record-response/recordResponse.queries";
import { upsertDatasetMetrics } from "@/models/feedback-task-model/dataset-metric/datasetMetric.queries.js";

export default {
  name: "QuestionsFormComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    recordId: {
      type: String,
      required: true,
    },
    recordStatus: {
      type: String,
      required: true,
    },
    initialInputs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      inputs: [],
      renderForm: 0,
      isError: false,
    };
  },
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    recordIdIndex() {
      return getRecordIndexByRecordId(this.recordId);
    },
    responseId() {
      return getRecordResponsesIdByRecordId({
        userId: this.userId,
        recordId: this.recordId,
      });
    },
    isFormUntouched() {
      return isEqual(this.initialInputs, this.inputs);
    },
    isSomeRequiredQuestionHaveNoAnswer() {
      return this.inputs.some(
        (input) =>
          input.is_required &&
          input.options.every(
            (option) => !option.value || option.value.length === 0
          )
      );
    },
    isRecordDiscarded() {
      return this.recordStatus === RECORD_STATUS.DISCARDED;
    },
    isRecordPending() {
      return this.recordStatus === RECORD_STATUS.PENDING;
    },
    isRecordSubmitted() {
      return this.recordStatus === RECORD_STATUS.SUBMITTED;
    },
    disableSubmitButton() {
      let isButtonDisable = false;
      switch (true) {
        case this.isRecordSubmitted:
          if (this.isFormUntouched || this.isSomeRequiredQuestionHaveNoAnswer) {
            isButtonDisable = true;
          }
          break;
        case this.isRecordDiscarded:
        case this.isRecordPending:
          if (this.isSomeRequiredQuestionHaveNoAnswer) isButtonDisable = true;
          break;
        default:
          isButtonDisable = false;
      }

      return isButtonDisable;
    },
  },
  watch: {
    isFormUntouched(isFormUntouched) {
      this.emitIsQuestionsFormUntouchedByBusEvent(isFormUntouched);
    },
  },
  async created() {
    this.COMPONENT_TYPE = COMPONENT_TYPE;
    this.onReset();

    // NOTE - Update dataset Metrics orm
    await this.refreshMetrics();
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);
  },
  destroyed() {
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onPressKeyboardShortCut({ code, shiftKey }) {
      switch (code) {
        case "Enter": {
          const elem = this.$refs.submitButton.$el;
          elem.click();
          break;
        }
        case "Space": {
          const elem = this.$refs.clearButton.$el;
          shiftKey && elem.click();
          break;
        }
        case "Backspace": {
          const elem = this.$refs.discardButton.$el;
          elem.click();
          break;
        }
        default:
      }
    },
    onChangeTextArea({ newOptions, idComponent }) {
      // TODO - remove this function when adding v-model on textArea component
      const component = this.inputs.find(({ id }) => id === idComponent);
      // NOTE - formatting to the standard options
      component.options = [{ ...newOptions, value: newOptions.text }];
    },
    onChangeMonoSelection({ newOptions, idComponent }) {
      // TODO - to remove when single label will use v-model
      const component = this.inputs.find(({ id }) => id === idComponent);
      component.options = newOptions;
    },
    async sendBackendRequest(responseValues) {
      try {
        let responseData = null;
        if (this.responseId) {
          responseData = await this.updateResponseValues(
            this.responseId,
            responseValues
          );
        } else {
          responseData = await this.createRecordResponses(
            this.recordId,
            responseValues
          );
        }
        const { data: updatedResponses } = responseData;

        if (updatedResponses) {
          this.updateResponsesInOrm({
            record_id: this.recordId,
            ...updatedResponses,
          });
        }
      } catch (error) {
        console.log(error);

        const message = "There was a problem to save the response";

        this.showNotificationComponent(message, "error");
      }
    },
    async onDiscard() {
      try {
        const responseValues = this.factoryInputsToResponseValues();

        await this.sendBackendRequest({
          status: RESPONSE_STATUS_FOR_API.DISCARDED,
          values: responseValues,
        });

        await this.refreshMetrics();

        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.DISCARDED
        );

        this.$emit("on-discard-responses");

        // TODO - reset only when we know that we fetch and computed all the necessary records data
        this.onReset();
      } catch (error) {
        console.log(error);
      }
    },
    async onSubmit() {
      if (this.isSomeRequiredQuestionHaveNoAnswer) {
        this.isError = true;
        return;
      }

      try {
        const responseValues = this.factoryInputsToResponseValues();

        await this.sendBackendRequest({
          status: RESPONSE_STATUS_FOR_API.SUBMITTED,
          values: responseValues,
        });

        await this.refreshMetrics();

        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.SUBMITTED
        );

        this.$emit("on-submit-responses");

        // TODO - reset only when we know that we fetch and computed all the necessary records data
        this.onReset();
      } catch (error) {
        console.log(error);
      }
    },
    async onClear() {
      try {
        const responseData =
          this.responseId &&
          (await this.deleteResponsesByResponseId(this.responseId));

        await deleteRecordResponsesByUserIdAndResponseId(
          this.userId,
          responseData?.data?.id
        );

        // NOTE - onClear event => the status change to PENDING
        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.PENDING
        );

        // NOTE - Update dataset Metrics orm
        await this.refreshMetrics();
        this.onReset();
      } catch (err) {
        console.log(err);
      }
    },
    onReset() {
      this.inputs = cloneDeep(this.initialInputs);
      this.isError = false;
      this.renderForm++;
    },
    onError(isError) {
      if (isError) {
        this.isError = true;
      } else {
        this.isError = false;
      }
    },
    async refreshMetrics() {
      const datasetMetrics = await this.fetchMetrics();

      const formattedMetrics = this.factoryDatasetMetricsForOrm(datasetMetrics);

      await upsertDatasetMetrics(formattedMetrics);
    },
    async deleteResponsesByResponseId(responseId) {
      return await this.$axios.delete(`/v1/responses/${responseId}`);
    },
    async fetchMetrics() {
      try {
        const { data } = await this.$axios.get(
          `/v1/me/datasets/${this.datasetId}/metrics`
        );

        return data;
      } catch (err) {
        console.log(err);
      }
    },
    factoryDatasetMetricsForOrm({ records, responses, user_id }) {
      const {
        count: responsesCount,
        submitted: responsesSubmitted,
        discarded: responsesDiscarded,
      } = responses;

      return {
        dataset_id: this.datasetId,
        user_id: user_id ?? this.userId,
        total_record: records?.count ?? 0,
        responses_count: responsesCount,
        responses_submitted: responsesSubmitted,
        responses_discarded: responsesDiscarded,
      };
    },
    async updateResponsesInOrm(responsesFromApi) {
      const newResponseToUpsertInOrm =
        this.formatResponsesApiForOrm(responsesFromApi);

      await upsertRecordResponses(newResponseToUpsertInOrm);
    },
    async updateResponseValues(responseId, responseByQuestionName) {
      return await this.$axios.put(
        `/v1/responses/${responseId}`,
        JSON.parse(JSON.stringify(responseByQuestionName))
      );
    },
    async createRecordResponses(recordId, responseByQuestionName) {
      return await this.$axios.post(
        `/v1/records/${recordId}/responses`,
        JSON.parse(JSON.stringify(responseByQuestionName))
      );
    },
    formatResponsesApiForOrm(responsesFromApi) {
      const formattedRecordResponsesForOrm = [];
      if (responsesFromApi.values) {
        if (Object.keys(responsesFromApi.values).length === 0) {
          // IF responses.value  is an empty object, init formatted responses with questions data
          this.inputs.forEach(
            ({ question: questionName, options: questionOptions }) => {
              formattedRecordResponsesForOrm.push({
                id: responsesFromApi.id,
                question_name: questionName,
                options: questionOptions,
                record_id: responsesFromApi.record_id,
                user_id: responsesFromApi.user_id ?? null,
              });
            }
          );
        } else {
          // ELSE responses.value is not an empty object, init formatted responses with questions data and corresponding responses
          Object.entries(responsesFromApi.values).map(
            ([questionName, newResponse]) => {
              const componentType =
                getComponentTypeOfQuestionByDatasetIdAndQuestionName(
                  this.datasetId,
                  questionName
                );
              let formattedOptions =
                getOptionsOfQuestionByDatasetIdAndQuestionName(
                  this.datasetId,
                  questionName
                );

              switch (componentType) {
                case COMPONENT_TYPE.SINGLE_LABEL:
                case COMPONENT_TYPE.RATING:
                  formattedOptions = formattedOptions.map((option) => {
                    if (option.text === newResponse.value) {
                      return { id: option.id, text: option.text, value: true };
                    }
                    return { id: option.id, text: option.text, value: false };
                  });
                  break;
                case COMPONENT_TYPE.FREE_TEXT:
                  formattedOptions = [
                    {
                      id: formattedOptions[0].id,
                      text: newResponse.value,
                      value: newResponse.value,
                    },
                  ];
                  break;
                default:
                  console.log(`The component type ${componentType} is unknown`);
                  return;
              }

              formattedRecordResponsesForOrm.push({
                id: responsesFromApi.id,
                question_name: questionName,
                user_id: responsesFromApi.user_id,
                record_id: responsesFromApi.record_id,
                options: formattedOptions,
              });
            }
          );
        }
      }
      return formattedRecordResponsesForOrm;
    },
    factoryInputsToResponseValues() {
      let responseByQuestionName = {};

      this.inputs.forEach((input) => {
        let selectedOption = null;
        switch (input.component_type) {
          case COMPONENT_TYPE.SINGLE_LABEL:
          case COMPONENT_TYPE.RATING:
            selectedOption = input.options?.find((option) => option.value);
            break;
          case COMPONENT_TYPE.FREE_TEXT:
            selectedOption = input.options[0];
            break;
          default:
            console.log(
              `The component type ${input.component_type} is unknown, the response can't be save`
            );
        }

        const isSelectedOptionNotEmpty = selectedOption ?? false;

        if (isSelectedOptionNotEmpty) {
          responseByQuestionName[input.name] = { value: selectedOption.text };
        }
      });
      return responseByQuestionName;
    },
    showNotificationComponent(message, typeOfToast) {
      Notification.dispatch("notify", {
        message,
        numberOfChars: message.length,
        type: typeOfToast,
      });
    },
    emitIsQuestionsFormUntouchedByBusEvent(isFormUntouched) {
      this.$emit("on-question-form-touched", !isFormUntouched);
      // TODO: Once notifications are centralized in one single point, we can remove this.
      this.$root.$emit("are-responses-untouched", isFormUntouched);
    },
  },
};
</script>

<style lang="scss" scoped>
.questions-form {
  display: flex;
  flex-direction: column;
  flex-basis: 37em;
  height: 100%;
  justify-content: space-between;
  border-radius: $border-radius-m;
  box-shadow: $shadow;
  &__header {
    display: flex;
    align-items: baseline;
    gap: $base-space * 2;
  }
  &__title {
    margin: 0;
    color: $black-87;
  }
  &__guidelines-link {
    margin: 0;
    @include font-size(13px);
    color: $black-37;
    a {
      color: $black-37;
      outline: 0;
      &:hover {
        color: $black-54;
      }
    }
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: $base-space * 3;
    overflow: auto;
  }
  &.--edited-form {
    border-color: palette(brown);
  }
}

.footer-form {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: $base-space * 2 $base-space * 3;
  border-top: 1px solid $black-10;
  &__left-area {
    display: inline-flex;
  }
  &__right-area {
    display: inline-flex;
    gap: $base-space * 2;
  }
}

.error-message {
  color: $danger;
}
</style>

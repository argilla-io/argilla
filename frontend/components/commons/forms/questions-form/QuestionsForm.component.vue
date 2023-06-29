<template>
  <form
    :key="renderForm"
    class="questions-form"
    :class="{ '--edited-form': !isFormUntouched }"
    @submit.prevent="onSubmit"
  >
    <div class="questions-form__content">
      <div class="questions-form__header">
        <p class="questions-form__title --heading5 --medium">
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
            >annotation guidelines <svgicon name="external-link" width="12" />
          </NuxtLink>
        </p>
      </div>
      <div
        class="form-group"
        v-for="(input, index) in inputs"
        ref="inputs"
        :key="input.id"
        @keydown.shift.arrow-down="updateFocusedQuestion(focusedQuestion + 1)"
        @keydown.shift.arrow-up="updateFocusedQuestion(focusedQuestion - 1)"
      >
        <TextAreaComponent
          v-if="input.component_type === COMPONENT_TYPE.FREE_TEXT"
          :title="input.question"
          :placeholder="input.placeholder"
          v-model="input.options[0].value"
          :useMarkdown="input.settings.use_markdown"
          :isRequired="input.is_required"
          :isFocused="checkIfQuestionIsFocused(index)"
          :description="input.description"
          @on-error="onError"
        />

        <SingleLabelComponent
          v-if="input.component_type === COMPONENT_TYPE.SINGLE_LABEL"
          :questionId="input.id"
          :title="input.question"
          v-model="input.options"
          :isRequired="input.is_required"
          :isFocused="checkIfQuestionIsFocused(index)"
          :description="input.description"
          :visibleOptions="input.settings.visible_options"
        />
        <MultiLabelComponent
          v-if="input.component_type === COMPONENT_TYPE.MULTI_LABEL"
          :questionId="input.id"
          :title="input.question"
          v-model="input.options"
          :isRequired="input.is_required"
          :isFocused="checkIfQuestionIsFocused(index)"
          :description="input.description"
          :visibleOptions="input.settings.visible_options"
        />

        <RatingComponent
          v-if="input.component_type === COMPONENT_TYPE.RATING"
          :title="input.question"
          v-model="input.options"
          :isRequired="input.is_required"
          :isFocused="checkIfQuestionIsFocused(index)"
          :description="input.description"
          @on-error="onError"
        />
        <RankingComponent
          v-if="input.component_type === COMPONENT_TYPE.RANKING"
          :title="input.question"
          :isRequired="input.is_required"
          :isFocused="checkIfQuestionIsFocused(index)"
          :description="input.description"
          v-model="input.options"
          :key="JSON.stringify(input.options)"
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
import "assets/icons/external-link";
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
      autofocusPosition: 0,
      focusedQuestion: 0,
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
    questionAreCompletedCorrectly() {
      const requiredQuestionsAreCompletedCorrectly = this.inputs
        .filter((input) => input.is_required)
        .every((input) => {
          if (input.component_type === COMPONENT_TYPE.FREE_TEXT) {
            return input.options[0]?.value.trim() != "";
          }

          if (input.component_type === COMPONENT_TYPE.RANKING) {
            return input.options.every((option) => option.rank);
          }

          return input.options.some((option) => option.is_selected);
        });

      const optionalQuestionsCompletedAreCorrectlyEntered = this.inputs
        .filter((input) => !input.is_required)
        .every((input) => {
          if (input.component_type === COMPONENT_TYPE.RANKING) {
            return (
              !input.options.some((option) => option.rank) ||
              input.options.every((option) => option.rank)
            );
          }

          return true;
        });

      return (
        requiredQuestionsAreCompletedCorrectly &&
        optionalQuestionsCompletedAreCorrectlyEntered
      );
    },
    isRecordDiscarded() {
      return this.recordStatus === RECORD_STATUS.DISCARDED;
    },
    isRecordSubmitted() {
      return this.recordStatus === RECORD_STATUS.SUBMITTED;
    },
    disableSubmitButton() {
      if (this.isRecordSubmitted)
        return this.isFormUntouched || !this.questionAreCompletedCorrectly;

      return !this.questionAreCompletedCorrectly;
    },
    currentInputsWithNoResponses() {
      return this.inputs.filter((input) => {
        if (
          input.component_type === COMPONENT_TYPE.RATING ||
          input.component_type === COMPONENT_TYPE.SINGLE_LABEL ||
          input.component_type === COMPONENT_TYPE.MULTI_LABEL
        ) {
          return input.options.every((option) => !option.is_selected);
        }

        if (input.component_type === COMPONENT_TYPE.RANKING) {
          return input.options.every((option) => !option.rank);
        }

        if (input.component_type === COMPONENT_TYPE.FREE_TEXT) {
          return !input.options[0]?.value.trim();
        }
      });
    },
  },
  watch: {
    isFormUntouched(isFormUntouched) {
      this.emitIsQuestionsFormUntouched(isFormUntouched);
    },
    autofocusPosition: {
      immediate: true,
      handler(newValue) {
        this.$nextTick(() => {
          if (!!newValue) {
            this.focusedQuestion = this.$refs.inputs.findIndex(
              (input) => input.contains(document.activeElement) || 0
            );
          }
        });
      },
    },
  },
  created() {
    this.COMPONENT_TYPE = COMPONENT_TYPE;
    this.onReset();
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);
  },
  destroyed() {
    this.emitIsQuestionsFormUntouched(true); // NOTE - ensure that on destroy, all parents and siblings have the flag well reinitiate
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
      if (!this.questionAreCompletedCorrectly) {
        this.isError = true;

        return;
      }

      try {
        const responseValues = this.factoryInputsToResponseValues();

        await this.sendBackendRequest({
          status: RESPONSE_STATUS_FOR_API.SUBMITTED,
          values: responseValues,
        });

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

        this.$emit("on-clear-responses");
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
    async deleteResponsesByResponseId(responseId) {
      return await this.$axios.delete(`/v1/responses/${responseId}`);
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
        // TODO - simplify if/else by one loop
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

          // TODO - remove both loop with only one loop over the form object ( this.inputs)
          // 1/ push formatted object corresponding to recordResponse which have been remove from api
          this.currentInputsWithNoResponses.forEach((input) => {
            formattedRecordResponsesForOrm.push({
              id: responsesFromApi.id,
              question_name: input.name,
              options: input.options,
              record_id: this.recordId,
              user_id: this.userId,
            });
          });

          // 2/ loop over the responseFromApi
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
                case COMPONENT_TYPE.MULTI_LABEL:
                case COMPONENT_TYPE.SINGLE_LABEL:
                case COMPONENT_TYPE.RATING:
                case COMPONENT_TYPE.RANKING:
                  debugger;
                  formattedOptions = formattedOptions.map((option) => {
                    const currentOptionsFromForm = this.inputs.find(
                      (input) => input.name === questionName
                    )?.options;
                    const currentOption = currentOptionsFromForm.find(
                      (currentOption) => currentOption.id === option.id
                    );

                    return {
                      ...currentOption,
                    };
                  });
                  break;
                case COMPONENT_TYPE.FREE_TEXT:
                  formattedOptions = [
                    {
                      id: formattedOptions[0].id,
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
        switch (input.component_type) {
          case COMPONENT_TYPE.MULTI_LABEL: {
            const selectedOptions =
              input.options?.filter((option) => option.is_selected) ?? false;

            if (selectedOptions?.length) {
              responseByQuestionName[input.name] = {
                value: selectedOptions.map((option) => option.value),
              };
            }
            break;
          }
          case COMPONENT_TYPE.SINGLE_LABEL:
          case COMPONENT_TYPE.RATING: {
            const selectedOption =
              input.options?.find((option) => option.is_selected) ?? false;

            if (selectedOption) {
              responseByQuestionName[input.name] = {
                value: selectedOption.value,
              };
            }
            break;
          }
          case COMPONENT_TYPE.FREE_TEXT: {
            const text = input.options[0]?.value.trim();

            if (text) {
              responseByQuestionName[input.name] = {
                value: text,
              };
            }

            break;
          }
          case COMPONENT_TYPE.RANKING: {
            if (input.options.some((o) => !o.rank)) return;

            responseByQuestionName[input.name] = {
              value: input.options,
            };

            break;
          }
          default:
            console.log(
              `The component type ${input.component_type} is unknown, the response can't be save`
            );
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
    emitIsQuestionsFormUntouched(isFormUntouched) {
      this.$emit("on-question-form-touched", !isFormUntouched);
      // TODO: Once notifications are centralized in one single point, we can remove this.
      this.$root.$emit("are-responses-untouched", isFormUntouched);
    },
    checkIfQuestionIsFocused(index) {
      return (
        this.recordStatus === RECORD_STATUS.PENDING &&
        index === this.focusedQuestion
      );
    },
    updateFocusedQuestion(index) {
      const numberOfQuestions = this.inputs.length;
      this.focusedQuestion = Math.min(
        numberOfQuestions - 1,
        Math.max(0, index)
      );
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
  min-width: 0;
  justify-content: space-between;
  border-radius: $border-radius-m;
  box-shadow: $shadow;
  &__header {
    align-items: baseline;
  }
  &__title {
    margin: 0 0 calc($base-space / 2) 0;
    color: $black-87;
  }
  &__guidelines-link {
    margin: 0;
    @include font-size(14px);
    color: $black-37;
    a {
      color: $black-37;
      outline: 0;
      text-decoration: none;
      &:hover,
      &:focus {
        text-decoration: underline;
      }
    }
  }
  &__content {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: $base-space * 4;
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

<template>
  <form class="questions-form" @submit.prevent="onSubmit" :key="renderForm">
    <div class="questions-form__content">
      <p class="questions-form__title --body1 --medium">Fill the fields</p>
      <div class="form-group" v-for="input in inputs" :key="input.id">
        <TextAreaComponent
          v-if="input.component_type === COMPONENT_TYPE.FREE_TEXT"
          :title="input.question"
          :optionId="`${input.name}_0`"
          :placeholder="input.placeholder"
          :initialOptions="input.options[0]"
          :isRequired="input.is_required"
          :isIcon="!!input.tooltip_message"
          :tooltipMessage="input.tooltip_message"
          :colorHighlight="colorAsterisk"
          @on-change-text-area="
            onChange({ newOptions: $event, idComponent: input.id })
          "
          @on-error="onError"
        />

        <SingleLabelComponent
          v-if="input.component_type === COMPONENT_TYPE.SINGLE_LABEL"
          :title="input.question"
          :initialOptions="input.options"
          :isRequired="input.is_required"
          :isIcon="!!input.tooltip_message"
          :tooltipMessage="input.tooltip_message"
          :colorHighlight="colorAsterisk"
          @on-change-single-label="
            onChange({ newOptions: $event, idComponent: input.id })
          "
          @on-error="onError"
        />

        <RatingComponent
          v-if="input.component_type === COMPONENT_TYPE.RATING"
          :title="input.question"
          :initialOptions="input.options"
          :isRequired="input.is_required"
          :isIcon="!!input.tooltip_message"
          :tooltipMessage="input.tooltip_message"
          :colorHighlight="colorAsterisk"
          @on-change-rating="
            onChange({ newOptions: $event, idComponent: input.id })
          "
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
        >
          <span v-text="'Discard'" />
        </BaseButton>
        <BaseButton
          ref="submitButton"
          type="submit"
          name="submitButton"
          value="submitButton"
          class="primary"
          :disabled="isFormUntouched || isError"
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
} from "@/models/feedback-task-model/record/record.queries";
import {
  getRecordResponsesIdByRecordId,
  upsertRecordResponses,
  deleteRecordResponsesByUserIdAndResponseId,
  isResponsesByUserIdExists,
} from "@/models/feedback-task-model/record-response/recordResponse.queries";

const STATUS_RESPONSE = Object.freeze({
  UPDATE: "UPDATE",
  CREATE: "CREATE",
  UNKNOWN: "UNKNOWN",
});
const TYPE_OF_EVENT = Object.freeze({
  ON_SUBMIT: "ON_SUBMIT",
  ON_DISCARD: "ON_DISCARD",
});
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
    initialInputs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      inputs: [],
      renderForm: 0,
      colorAsterisk: "black",
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
    isFormUntouched() {
      return isEqual(this.initialInputs, this.inputs);
    },
  },
  created() {
    this.COMPONENT_TYPE = COMPONENT_TYPE;
    this.formOnErrorMessage =
      "One of the required field is not answered. Please, answer before validate";
    this.onReset();
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);
  },
  destroyed() {
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onPressKeyboardShortCut({ code, ctrlKey }) {
      switch (code) {
        case "Enter": {
          const elem = this.$refs.submitButton.$el;
          elem.click();
          break;
        }
        case "Space": {
          const elem = this.$refs.clearButton.$el;
          ctrlKey && elem.click();
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
    onChange({ newOptions, idComponent }) {
      this.inputs = this.inputs.map((input) => {
        if (input.id === idComponent) {
          input.options = newOptions;
        }
        return input;
      });
    },
    async onDiscard() {
      try {
        // TODO - make the call here to discard the record
        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.DISCARDED
        );
        this.onEmitBusEventGoToRecordIndex(TYPE_OF_EVENT.ON_DISCARD);
      } catch (err) {
        console.log(err);
      }
    },
    async onSubmit() {
      const createOrUpdateResponse = isResponsesByUserIdExists(
        this.userId,
        this.recordId
      )
        ? STATUS_RESPONSE.UPDATE
        : STATUS_RESPONSE.CREATE;

      const isSomeRequiredQuestionHaveNoAnswer = this.inputs.some(
        (input) =>
          input.is_required &&
          input.options.every(
            (option) => !option.value || option.value.length === 0
          )
      );
      if (isSomeRequiredQuestionHaveNoAnswer) {
        this.isError = true;
        return;
      }
      let formattedSelectionOptionObject = {
        status: "submitted" // TODO: We need to do similar for discard
      };
      this.inputs.forEach((input) => {
        // NOTE - if there is a responseid for the input, means that it's an update. Otherwise it's a create

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


        formattedSelectionOptionObject.values = {
          ...formattedSelectionOptionObject.values,
          [input.name]: { value: selectedOption.text },
        };
      });

      const formattedRequestsToSend = {
        status: createOrUpdateResponse,
        responseByQuestionName: formattedSelectionOptionObject,
        ...(createOrUpdateResponse === STATUS_RESPONSE.UPDATE && {
          responseId: getRecordResponsesIdByRecordId({
            userId: this.userId,
            recordId: this.recordId,
          }),
        }),
        ...(createOrUpdateResponse === STATUS_RESPONSE.CREATE && {
          recordId: this.recordId,
        }),
      };

      try {
        await this.createOrUpdateRecordResponses(formattedRequestsToSend);
        // NOTE - onSubmit event => the status change to SUBMITTED
        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.SUBMITTED
        );
        this.onEmitBusEventGoToRecordIndex(TYPE_OF_EVENT.ON_SUBMIT);
      } catch (err) {
        console.log(err);
      }
    },
    onEmitBusEventGoToRecordIndex(typeOfEvent) {
      switch (typeOfEvent) {
        case TYPE_OF_EVENT.ON_SUBMIT:
        case TYPE_OF_EVENT.ON_DISCARD:
          this.$root.$emit("go-to-record-index", this.recordIdIndex + 1);
          break;
        default:
      }
    },
    async onClear() {
      const responseId = getRecordResponsesIdByRecordId({
        userId: this.userId,
        recordId: this.recordId,
      });

      try {
        const responseData =
          responseId && (await this.deleteResponsesByResponseId(responseId));

        await deleteRecordResponsesByUserIdAndResponseId(
          this.userId,
          responseData?.data?.id
        );

        // NOTE - onClear event => the status change to PENDING
        await updateRecordStatusByRecordId(
          this.recordId,
          RECORD_STATUS.PENDING
        );

        this.onReset();
      } catch (err) {
        console.log(err);
      }
    },
    onReset() {
      this.inputs = cloneDeep(this.initialInputs);
      this.isError = false;
      this.colorAsterisk = "black";
      this.renderForm++;
    },
    onError(isError) {
      if (isError) {
        this.colorAsterisk = "red";
        this.isError = true;
      } else {
        this.colorAsterisk = "black";
        this.isError = false;
      }
    },
    async deleteResponsesByResponseId(responseId) {
      return await this.$axios.delete(`/v1/responses/${responseId}`);
    },
    async createOrUpdateRecordResponses({
      status,
      responseId,
      responseByQuestionName,
    }) {
      try {
        let responseData = null;
        if (status === STATUS_RESPONSE.UPDATE) {
          responseData = await this.updateRecordResponses(
            responseId,
            responseByQuestionName
          );
        } else if (status === STATUS_RESPONSE.CREATE) {
          responseData = await this.createRecordResponses(
            this.recordId,
            responseByQuestionName
          );
        }

        const { data: updatedResponses } = responseData;

        if (updatedResponses) {
          this.updateResponsesInOrm({
            record_id: this.recordId,
            ...updatedResponses,
          });
        }
      } catch (err) {
        console.log(err);
        const message = "There was a problem to save the response";
        const typeOfToast = "error";
        this.showNotificationComponent(message, typeOfToast);
      }
    },
    async updateResponsesInOrm(responsesFromApi) {
      const newResponseToUpsertInOrm =
        this.formatResponsesApiForOrm(responsesFromApi);

      await upsertRecordResponses(newResponseToUpsertInOrm);
    },
    async updateRecordResponses(responseId, responseByQuestionName) {
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
      const newResponseToUpsertInOrm = Object.entries(
        responsesFromApi.values
      ).map(([questionName, newResponse]) => {
        const componentType =
          getComponentTypeOfQuestionByDatasetIdAndQuestionName(
            this.datasetId,
            questionName
          );
        let formattedOptions = getOptionsOfQuestionByDatasetIdAndQuestionName(
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

        const formattedResponse = {
          id: responsesFromApi.id,
          question_name: questionName,
          user_id: responsesFromApi.user_id,
          record_id: responsesFromApi.record_id,
          options: formattedOptions,
        };

        return formattedResponse;
      });

      return newResponseToUpsertInOrm;
    },
    showNotificationComponent(message, typeOfToast) {
      Notification.dispatch("notify", {
        message,
        numberOfChars: message.length,
        type: typeOfToast,
      });
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
  border-radius: $border-radius;
  box-shadow: $shadow;
  &__title {
    margin: 0;
    color: $black-87;
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: $base-space * 3;
    overflow: auto;
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

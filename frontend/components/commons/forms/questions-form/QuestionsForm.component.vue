<template>
  <form @submit.prevent="onSubmit" :key="renderForm">
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
    <div class="footer-form">
      <div class="error-message" v-if="isError">
        <i v-text="formOnErrorMessage" />
      </div>
      <div class="buttons-area">
        <BaseButton
          type="reset"
          class="primary outline small"
          @on-click="onReset"
          :disabled="isFormUntouched"
        >
          <span v-text="'Reset'" />
        </BaseButton>
        <BaseButton
          type="submit"
          class="primary small"
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
  getRecordResponsesIdByRecordId,
  upsertRecordResponses,
  isResponsesByUserIdExists,
} from "@/models/feedback-task-model/record-response/recordResponse.queries";

const STATUS_RESPONSE = Object.freeze({
  UPDATE: "UPDATE",
  CREATE: "CREATE",
  UNKNOWN: "UNKNOWN",
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
  created() {
    this.COMPONENT_TYPE = COMPONENT_TYPE;
    this.formOnErrorMessage =
      "One of the required field is not answered. Please, answer before validate";
    this.onReset();
  },
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    isFormUntouched() {
      return isEqual(this.initialInputs, this.inputs);
    },
  },
  methods: {
    onChange({ newOptions, idComponent }) {
      this.inputs = this.inputs.map((input) => {
        if (input.id === idComponent) {
          input.options = newOptions;
        }
        return input;
      });
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

      let formattedSelectionOptionObject = {};
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

      await this.createOrUpdateRecordResponses(formattedRequestsToSend);
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
    async createOrUpdateRecordResponses({
      status,
      responseId,
      responseByQuestionName,
    }) {
      let message = "";
      let typeOfToast = "successOrError";
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

        message = "Responses to the questions are saved!";
        typeOfToast = "success";

        const { data: updatedResponses } = responseData;
        if (updatedResponses) {
          this.updateResponsesInOrm(updatedResponses);
        }
      } catch (err) {
        console.log(err);
        message = "There was a problem to save the response";
        typeOfToast = "error";
      } finally {
        this.showNotificationComponent(message, typeOfToast);
      }
    },
    updateResponsesInOrm(responsesFromApi) {
      const newResponseToUpsertInOrm =
        this.formatResponsesApiForOrm(responsesFromApi);

      upsertRecordResponses(newResponseToUpsertInOrm);
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
form {
  display: flex;
  flex-direction: column;
  flex-basis: 40em;
  height: fit-content;
  gap: $base-space * 4;
  border: 2px solid #4c4ea3;
  border-radius: 8px;
  padding: $base-space * 4;
}

.footer-form {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
}

.buttons-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: $base-space * 8;
}

.error-message {
  color: $danger;
}
</style>

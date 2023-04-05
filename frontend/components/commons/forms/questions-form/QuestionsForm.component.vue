<template>
  <form @submit.prevent="onSubmit" :key="renderForm">
    <div class="form-group" v-for="input in inputs" :key="input.key">
      <TextAreaComponent
        v-if="input.componentType === PROPERTIES.FREE_TEXT"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        :isIcon="!!input.tooltipMessage"
        :tooltipMessage="input.tooltipMessage"
        :colorHighlight="colorAsterisk"
        @on-change-text-area="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
        @on-error="onError"
      />

      <SingleLabelComponent
        v-if="input.componentType === PROPERTIES.SINGLE_LABEL"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        :isIcon="!!input.tooltipMessage"
        :tooltipMessage="input.tooltipMessage"
        :colorHighlight="colorAsterisk"
        @on-change-single-label="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
        @on-error="onError"
      />

      <RatingComponent
        v-if="input.componentType === PROPERTIES.RATING"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        :isIcon="!!input.tooltipMessage"
        :tooltipMessage="input.tooltipMessage"
        :colorHighlight="colorAsterisk"
        @on-change-rating="
          onChange({ newOutputs: $event, idComponent: input.id })
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
          <span v-text="'Validate'" />
        </BaseButton>
      </div>
    </div>
    {{ inputs }}
  </form>
</template>

<script>
import { isEqual, cloneDeep } from "lodash";
import { PROPERTIES } from "./questionsForm.properties";

export default {
  name: "QuestionsFormComponent",
  props: {
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
    this.PROPERTIES = PROPERTIES;
    this.formOnErrorMessage =
      "One of the required field is not answered. Please, answer before validate";
    this.onReset();
  },
  computed: {
    isFormUntouched() {
      return isEqual(this.initialInputs, this.inputs);
    },
  },
  methods: {
    onChange({ newOutputs, idComponent }) {
      this.inputs = this.inputs.map((input) => {
        if (input.id === idComponent) {
          input.outputs = newOutputs;
        }
        return input;
      });
    },
    onSubmit() {
      console.log(this.inputs);
    },
    onReset() {
      this.inputs = cloneDeep(this.initialInputs);
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
  },
};
</script>

<style lang="scss" scoped>
form {
  display: flex;
  flex-direction: column;
  gap: $base-space * 4;
  border: 2px solid #4c4ea3;
  border-radius: 5px;
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
}

.error-message {
  color: $danger;
}
</style>

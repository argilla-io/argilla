<template>
  <form>
    <div class="form-group" v-for="input in inputs" :key="input.key">
      <TextAreaComponent
        v-if="input.componentType === PROPERTIES.FREE_TEXT"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        colorHighlight="red"
        @on-change-text-area="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
      />

      <SingleLabelComponent
        v-if="input.componentType === PROPERTIES.SINGLE_LABEL"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        colorHighlight="red"
        @on-change-rating="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
      />

      <RatingComponent
        v-if="input.componentType === PROPERTIES.RATING"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        colorHighlight="red"
        @on-change-rating="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
      />
    </div>
    {{ inputs }}
  </form>
</template>

<script>
import { cloneDeep } from "lodash";
import { PROPERTIES } from "./questionsForm.properties";

export default {
  name: "QuestionsFormComponent",
  props: {
    initialInput: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      inputs: cloneDeep(this.initialInput),
    };
  },
  created() {
    this.PROPERTIES = PROPERTIES;
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
  },
};
</script>

<style lang="scss" scoped>
form {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
}
</style>

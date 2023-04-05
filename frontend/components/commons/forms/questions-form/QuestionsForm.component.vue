<template>
  <form>
    <div class="form-group" v-for="input in inputs" :key="input.key">
      <RatingComponent
        v-if="input.componentType === 'RATING'"
        :title="input.question"
        :initialOutputs="input.outputs"
        :isRequired="input.required"
        colorHighlight="'blue'"
        @on-change-rating="
          onChange({ newOutputs: $event, idComponent: input.id })
        "
      />
    </div>
  </form>
</template>

<script>
import { cloneDeep } from "lodash";
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

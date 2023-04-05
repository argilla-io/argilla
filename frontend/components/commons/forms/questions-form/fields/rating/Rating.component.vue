<template>
  <div class="wrapper">
    <div class="title-area">
      <span
        :key="colorHighlight"
        v-text="title"
        v-required-field="isRequired ? { color: colorHighlight } : false"
      />
    </div>
    <div class="container">
      <div class="inputs-area">
        <div class="input-button" v-for="output in outputs" :key="output.id">
          <input
            type="checkbox"
            :name="output.text"
            :id="output.id"
            v-model="output.value"
            @change="
              onSelect({
                id: output.id,
                text: output.text,
                value: output.value,
              })
            "
          />
          <label
            class="label-text cursor-pointer"
            :class="{ 'label-active': output.value }"
            :for="output.id"
            v-text="output.text"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { cloneDeep } from "lodash";
export default {
  props: {
    title: {
      type: String,
    },
    initialOutputs: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
  data() {
    return {
      showAllLabels: true,
      outputs: cloneDeep(this.initialOutputs),
    };
  },
  methods: {
    onSelect({ id, value }) {
      this.outputs.map((output) => {
        if (output.id === id) {
          output.value = value;
        } else {
          output.value = false;
        }
        return output;
      });

      this.$emit("on-change-rating", this.outputs);
    },
    toggleShowAllLabels() {
      this.showAllLabels = !this.showAllLabels;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  .title-area {
  }
  .container {
    display: flex;
    .inputs-area {
      display: inline-flex;
      border-radius: 5em;
      border: 2px solid #aaaadd;
      background: #d8d8fa;
      gap: $base-space;
    }
  }
}

.label-text {
  display: flex;
  width: 100%;
  border-radius: 50em;
  height: 40px;
  background: #f0f0fe;
  outline: none;
  padding-left: 16px;
  padding-right: 16px;
  line-height: 40px;
  font-weight: 500;
  overflow: hidden;
  color: #4c4ea3;
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
}

input {
  display: none;
}

.label-active {
  color: white;
  background: #4c4ea3;
}
.cursor-pointer {
  cursor: pointer;
}
</style>

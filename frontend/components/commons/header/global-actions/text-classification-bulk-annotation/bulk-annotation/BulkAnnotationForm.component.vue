<template>
  <form @submit.prevent="onSubmit" @reset="onReset">
    <div class="form-group">
      <div v-for="input in clonedInputs" :key="input.key">
        <div class="item">
          <input
            type="checkbox"
            v-model="input.selected"
            :id="input.id"
            class="d-none"
          />
          <label :for="input.id" class="label-icon">
            <svgicon
              v-if="input.selected"
              name="close"
              width="15"
              height="15"
            />
          </label>
          <label
            :for="input.id"
            class="label-text"
            :class="input.selected ? '--selected' : null"
            >{{ input.label }}
            <span v-if="input.record_ids.size">
              ({{ input.record_ids.size }})
            </span>
          </label>
        </div>
      </div>
    </div>
    <div class="buttons-area">
      <BaseButton
        type="reset"
        class="primary outline small"
        :disabled="hasAnnotationsChanged"
      >
        Cancel
      </BaseButton>
      <BaseButton
        type="submit"
        class="primary small"
        :disabled="hasAnnotationsChanged"
      >
        Apply
      </BaseButton>
    </div>
  </form>
</template>

<script>
import _ from "lodash";
export default {
  name: "BulkAnnotationForm",
  props: {
    inputs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      clonedInputs: [],
    };
  },
  computed: {
    hasAnnotationsChanged() {
      return _.isEqual(this.inputs, this.clonedInputs);
    },
  },
  mounted() {
    this.resetCloneInputs();
  },
  methods: {
    onSubmit() {
      this.$emit("on-submit", this.clonedInputs);
    },
    onReset() {
      this.resetCloneInputs();
    },
    resetCloneInputs() {
      this.clonedInputs = structuredClone(this.inputs);
    },
  },
};
</script>

<style lang="scss" scoped>
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
}
.form-group {
  flex: 1;
  display: inline-flex;
  flex-direction: column;
  gap: $base-space;
  max-height: 220px;
  margin-top: 1em;
  overflow: auto;
}

.item {
  display: flex;
  min-height: 1em;
  align-items: center;
  gap: 0.5em;
}

.d-none {
  display: none;
}

.label-icon {
  flex-shrink: 0;
  cursor: pointer;
  border-radius: $border-radius;
  .svg-icon {
    &:hover {
      color: $black-87;
    }
  }
}

.label-text {
  cursor: pointer;
  background: #f0f0fe;
  border-radius: 8px;
  color: #4c4ea3;
  padding: calc($base-space / 2) $base-space;
  @include truncate;
  width: auto;
  @include font-size(13px);
  padding-right: $base-space * 2;
  font-weight: 500;
  span {
    @include font-size(12px);
  }
  &:hover {
    background: darken(#f0f0fe, 2%);
  }
  &.--selected {
    background: #4c4ea3;
    color: palette(white);
  }
}

.buttons-area {
  display: flex;
  gap: 0.5em;
  flex: 1;
  button {
    width: 100%;
    justify-content: center;
  }
}
</style>

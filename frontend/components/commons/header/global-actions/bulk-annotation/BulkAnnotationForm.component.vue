<template>
  <form @submit.prevent="onSubmit" @reset="onReset">
    <div class="form-group">
      <div v-for="input in inputs" :key="input.key">
        <div class="item">
          <input
            type="checkbox"
            v-model="input.selected"
            :id="input.id"
            class="d-none"
            @change="onChange(input)"
          />
          <div @click="onRemove(input)" class="label-icon">
            <svgicon
              v-if="input.record_ids.size"
              name="close"
              width="15"
              height="15"
            />
          </div>
          <label
            :for="input.id"
            class="label-text"
            :class="input.selected ? '--selected' : null"
          >
            {{ input.label }}
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
        :disabled="hasInputsChanged"
        v-html="'Cancel'"
      />
      <BaseButton
        type="submit"
        class="primary small"
        :disabled="hasInputsChanged"
        v-html="'Apply'"
      />
    </div>
  </form>
</template>

<script>
export default {
  name: "BulkAnnotationForm",
  props: {
    inputs: {
      type: Array,
      required: true,
    },
    hasInputsChanged: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    onSubmit() {
      this.$emit("on-submit", this.inputs);
    },
    onChange({ id, selected, record_ids, removed }) {
      this.$emit("on-change", {
        ID: id,
        VALUE: selected,
        RECORD_IDS: record_ids,
        REMOVED: removed,
      });
    },
    onReset() {
      this.$emit("on-reset");
    },
    onRemove({ id }) {
      this.$emit("on-remove", { ID: id });
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

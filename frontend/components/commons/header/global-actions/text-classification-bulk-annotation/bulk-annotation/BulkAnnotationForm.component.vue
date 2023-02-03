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
          <label :for="input.id">
            <svgicon
              name="close"
              v-if="input.selected"
              width="15"
              height="15"
              color="#9b9b9b"
            />
          </label>
          <label :for="input.id" class="label-text">{{ input.label }} </label>
          <span>
            {{ input.record_ids.length || "" }}
          </span>
        </div>
      </div>
    </div>
    <div class="buttons-area">
      <div class="toggle-reset-annottation">Ici toggle reset annotation</div>
      <div class="buttons-cancel-apply">
        <BaseButton type="reset" class="primary outline small" :disabled="false"
          >Cancel</BaseButton
        >
        <BaseButton type="submit" class="primary small" :disabled="false"
          >Apply</BaseButton
        >
      </div>
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
  },
  data() {
    return {
      clonedInputs: [],
    };
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
}
.form-group {
  flex: 1;
  display: inline-flex;
  flex-direction: column;
  gap: 1em;
  max-height: 220px;
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

.label-text {
  word-break: break-word;
}

.buttons-area {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  margin: 1em;
  .toggle-reset-annottation {
    background: crimson;
  }
  .buttons-cancel-apply {
    display: flex;
    justify-content: space-between;
  }
}
</style>

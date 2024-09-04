<template>
  <div class="feedback-wrapper">
    <p class="message" v-html="message" />
    <div class="buttons-area" v-if="isButtonLabels">
      <div class="button" v-for="{ label, value } in buttonLabels" :key="value">
        <BaseButton class="small" :id="label" @on-click="onClick(value)">
          {{ label }}
        </BaseButton>
      </div>
    </div>
    <BaseSpinner v-if="isLoading" />
  </div>
</template>

<script>
export default {
  name: "BaseFeedBackErrorComponent",
  props: {
    message: {
      type: String,
      required: true,
    },
    buttonLabels: {
      type: Array | null,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    isButtonLabels() {
      return this.buttonLabels?.length ?? false;
    },
  },
  methods: {
    onClick(value) {
      this.$emit("on-click", value);
    },
  },
};
</script>

<style lang="scss" scoped>
.feedback-wrapper {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  gap: $base-space * 2;
  padding: $base-space;
  margin-right: auto;
  background-color: rgba(255, 103, 95, 0.2);
  border-radius: $border-radius;
}

.message {
  @include font-size(14px);
  margin: 0;
  color: var(--fg-secondary);
  word-break: break-word;
}

.buttons-area {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 5px;
}

.button {
  color: white;
  background-color: rgba(255, 103, 95, 0.6);
  border-radius: $border-radius;
  button {
    padding: 6px 12px;
  }
}

:deep(a:hover) {
  color: var(--fg-primary);
}
</style>

<template>
  <div class="wrapper">
    <p class="message">{{ message }}</p>
    <div class="buttons-area" v-if="buttonLabels.length">
      <div class="button" v-for="{ label, value } in buttonLabels" :key="value">
        <BaseButton @click.prevent="onClick(value)">
          {{ label }}
        </BaseButton>
      </div>
    </div>
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
  },
  methods: {
    onClick(buttonValue) {
      this.$emit("on-click", buttonValue);
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: inline-flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 0.5em;
  background-color: rgb(255, 103, 95, 0.4);
  border-radius: $border-radius;
}

.message {
  @include font-size(14px);
  font-weight: 500;
  margin: inherit;
  color: $black-54;
  word-break: break-word;
}

.buttons-area {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 5px;
}

.button {
  border-radius: $border-radius;
  background-color: rgba(255, 103, 95, 0.6);
  color: white;
}
</style>

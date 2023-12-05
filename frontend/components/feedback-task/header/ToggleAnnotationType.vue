<template>
  <div class="annotation-type-switch">
    <button
      class="switch"
      :class="{ active: !value }"
      @click="handleChange(false)"
    >
      Focus
    </button>
    <button
      class="switch"
      :class="{ active: value }"
      @click="handleChange(true)"
    >
      Bulk
    </button>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      required: true,
    },
  },
  model: {
    prop: "value",
    event: "change",
  },
  methods: {
    handleChange(option) {
      this.$emit("change", option);
    },
  },
};
</script>

<style scoped lang="scss">
.annotation-type-switch {
  display: flex;
  align-items: center;
  border-radius: $border-radius;
  overflow: hidden;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 30px;
  background-color: $black-4;
  border: none;
  color: $black-54;
  cursor: pointer;
  outline: none;
  transition: background-color 0.4s;
}

.switch.active {
  background-color: $black-54;
  color: palette(white);
}
</style>

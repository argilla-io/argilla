<template>
  <div class="container">
    <div class="inputs-area">
      <div class="input-button" v-for="option in options" :key="option.id">
        <input
          type="checkbox"
          :name="option.text"
          :id="option.id"
          v-model="option.value"
          @change="$emit('on-select', option)"
        />
        <label
          class="label-text cursor-pointer"
          :class="{ 'label-active': option.value }"
          :for="option.id"
          v-text="option.text"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MonoSelectionRenderStyle2Component",
  props: {
    options: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  .inputs-area {
    display: inline-flex;
    gap: $base-space;
    border-radius: 5em;
    background: transparent;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}
.label-text {
  display: flex;
  width: 100%;
  border-radius: 50em;
  height: 40px;
  background: palette(purple, 800);
  outline: none;
  padding-left: 16px;
  padding-right: 16px;
  line-height: 40px;
  font-weight: 500;
  overflow: hidden;
  color: palette(purple, 200);
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 8%);
  }
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

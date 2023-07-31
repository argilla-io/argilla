<template>
  <div class="container">
    <div class="inputs-area">
      <div class="input-button" v-for="option in options" :key="option.id">
        <input
          type="checkbox"
          :name="option.value"
          :id="option.id"
          v-model="option.isSelected"
          @change="onSelect(option)"
        />
        <label
          class="label-text cursor-pointer"
          :class="{ 'label-active': option.isSelected }"
          :for="option.id"
          v-text="option.value"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RatingMonoSelectionComponent",
  props: {
    options: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
  },
  methods: {
    onSelect({ id, isSelected }) {
      this.options.map((option) => {
        if (option.id === id) {
          option.isSelected = isSelected;
        } else {
          option.isSelected = false;
        }
        return option;
      });

      this.$emit("on-change", this.options);
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
    border-radius: $border-radius-rounded;
    border: 1px solid #cdcdff;
    background: #e0e0ff;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}
.label-text {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  border-radius: $border-radius-rounded;
  height: $base-space * 4;
  min-width: $base-space * 4;
  padding-inline: $base-space;
  outline: none;
  background: palette(purple, 800);
  color: palette(purple, 200);
  font-weight: 500;
  overflow: hidden;
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

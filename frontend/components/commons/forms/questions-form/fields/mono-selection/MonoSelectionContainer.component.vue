<template>
  <MonoSelectionRenderStyle1Component
    v-if="styleType === COMPONENT_STYLE.STYLE_1"
    :options="options"
    @on-select="onSelect"
  />
</template>

<script>
import { COMPONENT_STYLE } from "./monoSelection.properties";

export default {
  name: "MonoSelectionContainerComponent",
  props: {
    options: {
      type: Array,
      required: true,
    },
    styleType: {
      type: String,
      default: () => COMPONENT_STYLE.STYLE_1,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
  },
  created() {
    this.COMPONENT_STYLE = COMPONENT_STYLE;
  },
  methods: {
    onSelect({ id, value }) {
      this.options.map((option) => {
        if (option.id === id) {
          option.value = value;
        } else {
          option.value = false;
        }
        return option;
      });

      this.$emit("on-change", this.options);
    },
  },
};
</script>

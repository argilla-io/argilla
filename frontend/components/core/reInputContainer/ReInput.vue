<template>
  <input
    class="re-input"
    :type="type"
    :name="name"
    :value="value"
    :disabled="disabled"
    :required="required"
    :placeholder="placeholder"
    :maxlength="maxlength"
    :readonly="readonly"
    @focus="onFocus"
    @blur="onBlur"
    @input="onInput"
    @keydown.up="onInput"
    @keydown.down="onInput"
  />
</template>

<script>
import common from "./common";
import getClosestVueParent from "~/components/core/utils/getClosestVueParent";

export default {
  mixins: [common],
  props: {
    type: {
      type: String,
      default: "text",
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.parentContainer = getClosestVueParent(
        this.$parent,
        "re-input-container"
      );

      if (!this.parentContainer) {
        this.$destroy();

        throw new Error("You should wrap the re-input in a re-input-container");
      }

      this.parentContainer.inputInstance = this;
      this.setParentDisabled();
      this.setParentRequired();
      this.setParentPlaceholder();
      this.handleMaxLength();
      this.updateValues();
    });
  },
};
</script>

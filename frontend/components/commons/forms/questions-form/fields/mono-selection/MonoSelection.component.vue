<template>
  <div class="container" :style="cssVars">
    <div class="inputs-area">
      <div class="input-button" v-for="option in options" :key="option.id">
        <input
          type="checkbox"
          :name="option.text"
          :id="option.id"
          v-model="option.value"
          @change="
            onSelect({
              id: option.id,
              text: option.text,
              value: option.value,
            })
          "
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
import { cloneDeep } from "lodash";
import "assets/icons/info";

export default {
  name: "MonoSelectionComponent",
  props: {
    initialOptions: {
      type: Array,
      required: true,
    },
    backgroundColor: {
      type: String,
      default: () => "transparent",
    },
    borderColor: {
      type: String,
      default: () => "none",
    },
  },
  data() {
    return {
      options: cloneDeep(this.initialOptions),
    };
  },
  computed: {
    cssVars() {
      return {
        "--background-color": this.backgroundColor,
        "--border-color": this.borderColor,
      };
    },
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

<style lang="scss" scoped>
 .container {
   display: flex;
   .inputs-area {
     display: inline-flex;
     gap: $base-space;
     border-radius: 5em;
     border: 1px solid var(--border-color);
     background: var(--background-color);
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

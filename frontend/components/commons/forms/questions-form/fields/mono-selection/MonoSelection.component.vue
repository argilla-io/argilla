<template>
  <div class="wrapper" :style="cssVars">
    <div class="title-area --body1">
      <span
        :key="colorHighlight"
        v-text="title"
        v-required-field="isRequired ? { color: colorHighlight } : false"
      />
      <TooltipComponent
        class="info-icon"
        v-if="isIcon"
        :message="tooltipMessage"
        direction="bottom"
      >
        <svgicon class="icon" name="info" width="22" height="22" />
      </TooltipComponent>
    </div>
    <div class="container">
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
  </div>
</template>

<script>
import { cloneDeep } from "lodash";
import "assets/icons/info";

export default {
  name: "MonoSelectionComponent",
  props: {
    title: {
      type: String,
    },
    initialOptions: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    isIcon: {
      type: Boolean,
      default: () => false,
    },
    tooltipMessage: {
      type: String,
      default: () => "",
    },
    colorHighlight: {
      type: String,
      default: () => "red",
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
      showAllLabels: true,
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
    toggleShowAllLabels() {
      this.showAllLabels = !this.showAllLabels;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  .title-area {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: $black-37;
  }
  .container {
    display: flex;
    .inputs-area {
      display: inline-flex;
      border-radius: 5em;
      border: 2px solid var(--border-color);
      background: var(--background-color);
      gap: $base-space;
    }
  }
}

.label-text {
  display: flex;
  width: 100%;
  border-radius: 50em;
  height: 40px;
  background: #f0f0fe;
  outline: none;
  padding-left: 16px;
  padding-right: 16px;
  line-height: 40px;
  font-weight: 500;
  overflow: hidden;
  color: #4c4ea3;
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
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

.icon {
  color: $black-37;
}

.info-icon {
  display: flex;
  flex-basis: 37px;
}

span {
  word-break: break-word;
}
</style>

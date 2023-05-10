<template>
  <div class="wrapper" :style="cssVars">
    <div class="title-area --body2">
      <span
        :key="colorHighlight"
        v-text="title"
        v-optional-field="isRequired ? false : true"
      />

      <BaseIconWithBadge
        class="icon-info"
        v-if="isIcon"
        icon="info"
        :id="`${title}MonoSelection`"
        :show-badge="false"
        iconColor="rgba(0, 0, 0, 0.37)"
        badge-vertical-position="top"
        badge-horizontal-position="right"
        badge-border-color="white"
        v-tooltip="{ content: tooltipMessage, backgroundColor: '#FFF' }"
      />
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
    color: $black-87;
    font-weight: 500;
  }
  .container {
    display: flex;
    .inputs-area {
      display: inline-flex;
      gap: $base-space;
      border-radius: 5em;
      border: 1px solid var(--border-color);
      background: var(--background-color);
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

.icon-info {
  margin: 0;
  padding: 0;
  overflow: inherit;
  &[data-title] {
    position: relative;
    overflow: visible;
    &:before,
    &:after {
      margin-top: 0;
    }
  }
}
</style>

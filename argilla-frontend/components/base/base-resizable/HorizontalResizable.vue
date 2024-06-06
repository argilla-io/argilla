<template>
  <div class="resizable">
    <div class="resizable__up"><slot name="up" /></div>

    <div v-if="isDownExpanded" class="resizable__bar" ref="resizableBar">
      <div class="resizable__bar__inner" />
    </div>
    <div v-else class="resizable__bar__inner--no-hover" ref="resizableBar" />

    <div class="resizable__down">
      <div class="resizable__header">
        <slot name="downHeader" />

        <BaseButton @click="isDownExpanded = !isDownExpanded">
          <svgicon
            v-if="isDownExpanded"
            name="chevron-down"
            width="20"
            height="20"
          />

          <svgicon
            v-if="!isDownExpanded"
            name="chevron-right"
            width="20"
            height="20"
          />
        </BaseButton>
      </div>
      <slot v-if="isDownExpanded" name="down" />
    </div>
  </div>
</template>

<script>
import "assets/icons/chevron-right";
import "assets/icons/chevron-down";
import { useResizable } from "./useResizable";
import BaseButton from "../base-button/BaseButton.vue";

const EVENT = {
  MOUSE_EVENT: "mousemove",
  MOUSE_UP: "mouseup",
  MOUSE_DOWN: "mousedown",
};

export default {
  components: { BaseButton },
  props: {
    id: {
      type: String,
      default: "h-rz",
    },
  },
  data() {
    return {
      isDownExpanded: false,
      upSidePrevPosition: {
        clientY: 0,
        height: 0,
      },
      resizer: null,
      upSide: null,
      downSide: null,
    };
  },
  watch: {
    isDownExpanded() {
      if (this.isDownExpanded) {
        this.upSide.style.height = "60%";
      } else {
        this.upSide.style.height = "100%";
      }

      this.$nextTick(() => {
        this.setPosition(`${this.upSide.getBoundingClientRect().height}px`);
      });
    },
  },
  mounted() {
    this.resizer = this.$refs.resizableBar;
    this.upSide = this.resizer.previousElementSibling;
    this.downSide = this.resizer.nextElementSibling;

    this.limitElementHeight(this.upSide);

    this.resizer.addEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);

    const savedPosition = this.getPosition();
    if (savedPosition) {
      this.upSide.style.height = savedPosition;
    }
  },
  destroyed() {
    this.resizer.removeEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);
  },
  methods: {
    limitElementHeight(element) {
      element.style["max-height"] = "100%";
      element.style["min-height"] = "50%";
    },
    savePositionOnStartResizing(e) {
      this.upSidePrevPosition = {
        clientY: e.clientY,
        height: this.upSide.getBoundingClientRect().height,
      };
    },
    resize(e) {
      const dY = e.clientY - this.upSidePrevPosition.clientY;
      const proportionalHeight = (this.upSidePrevPosition.height + dY) * 100;
      const parentHeight =
        this.resizer.parentNode.getBoundingClientRect().height;

      const newHeight = proportionalHeight / parentHeight;

      this.upSide.style.height = `${newHeight}%`;
    },
    mouseMoveHandler(e) {
      this.resize(e);
    },
    mouseUpHandler() {
      this.setPosition(`${this.upSide.getBoundingClientRect().height}px`);

      document.removeEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.removeEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
    },
    mouseDownHandler(e) {
      this.savePositionOnStartResizing(e);

      document.addEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.addEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
    },
  },
  setup(props) {
    return useResizable(props);
  },
};
</script>
<style lang="scss" scoped>
$card-primary-color: #e0e0ff;
$card-secondary-color: palette(purple, 200);

.resizable {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  height: 100%;
  width: 100%;

  &__header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  &__up {
    align-items: center;
    display: flex;
    justify-content: center;
  }

  &__down {
    flex: 1;
    align-items: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  &__bar {
    height: $base-space;
    width: 100%;
    display: flex;
    align-items: center;
    cursor: ns-resize;

    &__inner {
      width: 100%;
      border-bottom: thick solid lightgray;
      border-width: 1px;

      &:hover {
        border-width: 2px;
      }
    }

    &__inner--no-hover {
      width: 100%;
      border-bottom: thick solid lightgray;
      border-width: 1px;
    }

    &:hover {
      background-color: $card-primary-color;
    }
  }
}
</style>

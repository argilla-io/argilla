<template>
    <div class="sidebar">
        <div class="sidebar__actions">
            <a href="#" @click.prevent="logout()" data-title="close session">
            <svgicon
                name="logout"
            ></svgicon>
            </a>
            <a href="#" @click.prevent data-title="annotation mode">
              <ReSwitch
                class="sidebar__actions__switch"
                v-model="annotationMode"
                @change="$emit('onChangeMode')"
                ></ReSwitch
              >
            </a>
            <a href="#" @click.prevent="refresh()" data-title="refresh">
            <svgicon
                name="refresh"
            ></svgicon>
            </a>
        </div>
        <div class="sidebar__info">
            <a class="sidebar__info__button" href="#" v-for="sidebarInfo in sidebarInfoOptions" :key="sidebarInfo.id" :data-title="sidebarInfo.tooltip" :class="visibleSidebarInfo === sidebarInfo.id ? 'active' : ''" @click.prevent="showSidebarInfo(sidebarInfo.id)">
            <svgicon
                class="sidebar__info__chev"
                :name="visibleSidebarInfo === sidebarInfo ? 'chev-right' : 'chev-left'"
            ></svgicon>
            <svgicon
                :name="sidebarInfo.icon"
            ></svgicon>
            </a>
        </div>
    </div>
</template>

<script>
import "assets/icons/logout";
import "assets/icons/refresh";
import "assets/icons/progress";
import "assets/icons/metrics";
import "assets/icons/chev-left";
import "assets/icons/chev-right";
export default {
  data: () => {
    return {
      annotationMode: false,
      sidebarInfoOptions: [
        {
          id: "progress",
          tooltip: "annotation progress",
          icon: "progress"
        },
        {
          id: "stats",
          tooltip: "stats",
          icon: "metrics"
        },
      ],
      visibleSidebarInfo: undefined,
    }
  },
  methods: {
    showSidebarInfo(info) {
      this.visibleSidebarInfo = info;
      this.$emit('showSidebarInfo', info);
    },
  },
  mounted() {
    this.annotationMode =
      this.$route.query.allowAnnotation === "true" ? true : false;
  },
};
</script>

<style lang="scss" scoped>
$sidebar-button-size: 45px;
.sidebar {
  background: palette(grey, verylight);
  width: $sidebar-button-size;
  z-index: 2;
  a {
    position: relative;
  }
  .svg-icon {
    fill: $primary-color;
    display: block;
    height: $sidebar-button-size;
    text-align: center;
    line-height: $sidebar-button-size;
    margin: auto;
  }
  &__actions {
    margin-bottom: 3.8em;
    &__switch {
      margin: 1em auto;
    }
  }
  &__info {
    &__chev {
      left: 5px;
      width: 5px;
      margin-right: 0;
      stroke-width: 2
    }
    .svg-icon {
      & + .svg-icon {
        margin-right: auto;
        margin-left: 0;
      }
    }
    &__button {
      display: flex;
      &.active {
        background: white;
        outline: none;
      }
    }
  }
}
a[data-title] {
  @extend %hastooltip;
  &:after {
    top: 1em;
    right: calc(100% - 5px);
    transform: none;
    background: $font-secondary-dark;
    color: white;
    border: none;
  }
}
</style>


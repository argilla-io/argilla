<template>
  <span
    :key="recordStatus"
    :class="['status-tag', getStatusInfo.class]"
    :title="getStatusInfo.name"
    ><span class="bullet"></span>
    <span>{{ getStatusInfo.name }}</span>
  </span>
</template>

<script>
export default {
  props: {
    recordStatus: {
      type: String,
    },
  },
  computed: {
    getStatusInfo() {
      switch (this.recordStatus) {
        case "pending":
          return {
            name: this.$t("recordStatus.pending"),
            icon: null,
            class: "--pending",
          };
        case "draft":
          return {
            name: this.$t("recordStatus.draft"),
            icon: null,
            class: "--draft",
          };

        case "discarded":
          return {
            name: this.$t("recordStatus.discarded"),
            icon: "discard",
            class: "--discarded",
          };

        case "submitted":
          return {
            name: this.$t("recordStatus.submitted"),
            icon: "validate",
            class: "--submitted",
          };
      }
    },
  },
};
</script>

<style scoped lang="scss">
%bullet {
  content: "";
  display: inline-block;
  width: $base-space;
  height: $base-space;
  border-radius: $border-radius-rounded;
}
.status-tag {
  display: flex;
  align-items: center;
  gap: $base-space;
  @include font-size(13px);
  font-weight: 500;

  &.--discarded {
    color: $discarded-color;
    .bullet:before {
      @extend %bullet;
      background: $discarded-color;
    }
  }
  &.--submitted {
    color: $submitted-color;
    .bullet:before {
      @extend %bullet;
      background: $submitted-color;
    }
  }
  &.--pending {
    color: $pending-color;
    .bullet:before {
      @extend %bullet;
      background: $pending-color;
    }
  }
  &.--draft {
    color: $draft-color;
    .bullet:before {
      @extend %bullet;
      background: $draft-color;
    }
  }
}
</style>

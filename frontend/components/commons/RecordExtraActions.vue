<template>
  <div class="record__extra-actions">
    <div v-if="hasMetadata" @click="$emit('onShowMetadata')">
      <span>View metadata</span>
    </div>

    <div
      v-for="status in allowedStatusActions"
      :key="status.key"
      @click="onChangeRecordStatus(status.key)"
    >
      <span v-if="status.isActive" :class="status.class">{{
        status.activeName
      }}</span>
      <span v-else>{{ status.name }}</span>
    </div>
  </div>
</template>

<script>
import { BaseRecord } from "@/models/Common";

export default {
  props: {
    annotationMode: {
      type: Boolean,
      default: false,
    },
    record: {
      type: BaseRecord,
      required: true,
    },
  },
  data: () => ({
    statusActions: [
      {
        name: "Discard",
        activeName: "Discarded",
        key: "Discarded",
        class: "discard",
      },
    ],
  }),
  computed: {
    hasMetadata() {
      const metadata = this.record.metadata;
      return metadata && Object.values(metadata).length;
    },
    recordStatus() {
      return this.record.status;
    },
    allowedStatusActions() {
      if (!this.annotationMode) {
        return [];
      }

      return this.statusActions.map((status) => ({
        ...status,
        isActive: this.recordStatus === status.key,
      }));
    },
  },
  methods: {
    onChangeRecordStatus(status) {
      if (this.record.status !== status) {
        this.$emit("onChangeRecordStatus", status);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  &__extra-actions {
    @include font-size(13px);
    text-align: right;
    .annotate {
      color: $success;
    }
    .discard {
      color: $error;
    }
    > div {
      margin-top: 1em;
    }
    > * + *:before {
      content: "";
      margin: auto 1em;
      height: 1em;
      width: 1px;
      background: $font-medium-color;
      vertical-align: middle;
      display: inline-block;
    }
    & > * {
      display: inline-block;
      cursor: pointer;
    }
  }
}
</style>

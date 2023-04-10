<template>
  <HeaderAndTopAndOneColumn>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent />
    </template>
    <template v-slot:sidebar-right>
      <SidebarFeedbackTaskComponent />
    </template>
    <template v-slot:center>
      <CenterFeedbackTaskContent />
    </template>
  </HeaderAndTopAndOneColumn>
</template>

<script>
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
  },
};
</script>

<template>
  <main>
    <h1>HF login</h1>

    <div>
      <h2>{{ user }}</h2>
      <h2>{{ space }}</h2>
    </div>
  </main>
</template>
<script>
import { useHuggingFaceHost } from "~/v1/infrastructure/services/useHuggingFaceHost";

export default {
  name: "hf-login",
  data() {
    return {
      user: "",
      space: "",
    };
  },
  mounted() {
    const space = this.isRunningOnHuggingFace();
    this.user = space.user;
    this.space = space.space;
  },
  setup() {
    return useHuggingFaceHost();
  },
};
</script>

<template></template>

<script>
export default {
  middleware({ route, redirect }) {
    if (route.params.id) {
      const newRoute = encodeURIComponent(route.params.id);
      redirect(newRoute);
    } else {
      redirect("/");
    }
  },
};
</script>

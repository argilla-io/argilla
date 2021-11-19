<template>
    <div class="results-pagination-end">
        <svgicon width="40" height="40" name="pagination-end" />
        <p>You have reached the current record limit (10,000). To view more records please refine your query</p>
    </div>
</template>
<script>
import "assets/icons/pagination-end";
export default {

}
</script>

<style lang="scss" scoped>
.results-pagination-end {
    animation: fade 1s;
    padding: 3em 3em 0 3em;
    display: flex;
    align-items: center;
    font-weight: lighter;
    .svg-icon {
        margin-right: 2em;
    }
}
@keyframes fade {
    0% {
        opacity: 0
    }
    100% {
        opacity: 1;
    }
}
</style>


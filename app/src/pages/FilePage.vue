<template>
  <FileCaseForm :next-case-no="caseCount" @filed="onFiled" />
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import FileCaseForm from "../components/FileCaseForm.vue";
import { caseCount } from "../lib/client";

const router = useRouter();

// After a successful filing, send them to the docket so they can watch
// the ruling land rather than staying on an emptied-out form.
function onFiled() {
  router.push({ name: "docket" });
}
</script>

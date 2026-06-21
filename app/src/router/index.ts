import { createRouter, createWebHistory } from "vue-router";
import FilePage from "../pages/FilePage.vue";
import DocketPage from "../pages/DocketPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "file", component: FilePage },
    { path: "/docket", name: "docket", component: DocketPage },
  ],
});

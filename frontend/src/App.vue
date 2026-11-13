/**
 * Main App Component
 */

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useMeritsStore } from '@/stores/merits';
import { useAirportStore } from '@/stores/airport';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';

const authStore = useAuthStore();
const meritsStore = useMeritsStore();
const airportStore = useAirportStore();
const routerInstance = useRouter();

onMounted(async () => {
  // Initialize stores
  await Promise.all([
    authStore.fetchUser(),
    meritsStore.fetchBalance(),
    meritsStore.fetchCatalog(),
    airportStore.fetchAirports(),
    airportStore.fetchGrades(),
    airportStore.fetchMyClearances(),
  ]);

  // Check if we're on a protected route
  routerInstance.beforeEach((to, _from, next) => {
    const requiresAuth = to.meta.requiresAuth;
    const minLevel = (to.meta.minIdentityLevel as number) || 0;

    if (requiresAuth && !authStore.isAuthenticated) {
      next('/login?redirect=' + to.fullPath);
      return;
    }

    if (authStore.isAuthenticated && minLevel > authStore.identityLevel) {
      next('/upgrade-identity?required=' + minLevel);
      return;
    }

    next();
  });
});
</script>

<template>
  <div class="app min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <TheHeader />
    
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <TheFooter />
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
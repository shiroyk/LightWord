<template>
<v-app id="index">
  <homebar v-if="$route.meta.requireAuth"></homebar>
  <v-content>
    <router-view/>
  </v-content>

</v-app>
</template>

<script>

import homeBar from '@/components/base/homeBar'

export default {
  name: 'App',
  components: {
    homebar: homeBar
  }
}
</script>

<style>
</style>
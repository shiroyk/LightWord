import Vue from 'vue';
import Vuetify from 'vuetify/lib';
import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify);

import zhHans from 'vuetify/es5/locale/zh-Hans'

export default new Vuetify({
    lang: {
      locales: { zhHans },
      current: 'zhHans',
    },
    theme: {
        themes: {
          light: {
            primary: colors.blue.darken3,
            secondary: colors.blue.darken1,
            accent: colors.blue.darken1,
          },
          dark: {
            primary: colors.blue.darken3,
            secondary: colors.grey.lighten1,
            accent: colors.blue.darken1,
          },
        },
      },
});

<template>
  <div class="navContainer">
    <v-navigation-drawer
      width="200"
      v-model="drawer"
      mobile-break-point="600"
      :mini-variant="$vuetify.breakpoint.smAndUp"
      :clipped="$vuetify.breakpoint.smAndUp"
      app
    >
      <v-list>
        <v-list-item-group mandatory color="secondary">
          <v-list-item v-for="(item, i) in items" :key="i" link :to="{path: item.router}">
            <v-list-item-icon>
              <v-icon>{{item.icon}}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
        <v-list-item ripple @click="setTheme">
          <v-list-item-icon>
            <v-icon>{{$vuetify.theme.dark ? 'mdi-brightness-4':'mdi-brightness-7'}}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>{{$vuetify.theme.dark ? 'dark':'light'}}</v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar :clipped-left="$vuetify.breakpoint.smAndUp" app dark color="primary">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title class="ml-0 pl-4">
        <span>{{$route.meta.title}}</span>
      </v-toolbar-title>
      <v-spacer />
      <v-btn icon @click="statistics = !statistics">
        <v-icon>mdi-chart-line</v-icon>
      </v-btn>
      <v-dialog v-model="statistics" width="30rem">
        <v-card>
          <v-card-title class="accent">
            <span style="color:white">Statistics</span>
            <v-btn icon dark small absolute top right @click="statistics = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-text-field
              v-model="search"
              clearable
              label="Search"
              single-line
              hide-details
            ></v-text-field>
            <v-data-table
              :headers="headers"
              :items="desserts"
              item-key="name"
              :search="search"
              :loading="loading"
              :mobile-breakpoint="NaN"
              loading-text="Loading... Please wait"
            ></v-data-table>
            
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-app-bar>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  props: {
    source: String
  },
  data: () => ({
    statistics: false,
    drawer: null,
    loading: false,
    search: null,
    desserts: [],
    headers: [
      { text: "Word", value: "word" },
      { text: "Correct", value: "correct", filterable: false },
      { text: "Wrong", value: "wrong", filterable: false }
    ],
    items: [
      {
        icon: "mdi-home",
        text: "Home",
        router: "/home"
      },
      {
        icon: "mdi-cards",
        text: "Practice",
        router: "/practice"
      },
      {
        icon: "mdi-cog",
        text: "Setting",
        router: "/setting"
      },
      {
        icon: "mdi-help-circle",
        text: "Help",
        router: "/help"
      }
    ]
  }),
  computed: {
    ...mapState({
      theme: state => state.theme.theme
    })
  },
  methods: {
    getUserword() {
      if (this.desserts.length > 0) return;

      this.loading = true;
      this.$axios
        .get("/user/word", {})
        .then(response => {
          this.desserts = response.data;
          this.loading = false;
        })
        .catch(error => {
          console.log(error.data);
        });
    },
    setTheme() {
      if (this.theme == "dark") {
        this.$vuetify.theme.dark = false;
        this.$store.commit("setTheme", "light");
      } else {
        this.$vuetify.theme.dark = true;
        this.$store.commit("setTheme", "dark");
      }
    },
    readTheme() {
      if (this.theme == "dark") {
        this.$vuetify.theme.dark = true;
      } else {
        this.$vuetify.theme.dark = false;
      }
    }
  },
  created() {
    this.readTheme();
  },
  mounted() {
    this.getUserword();
  }
};
</script>
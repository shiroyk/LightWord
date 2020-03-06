<template>
  <v-container>
    <chart></chart>
    <v-row dense class="mx-auto" style="max-width: 60rem">
      <v-col v-for="card in cards" :key="card.title" :cols="card.flex">
        <v-card>
          <v-card-title v-text="card.title"></v-card-title>
          <v-card-text class="text--primary">
            <div>{{card.content}}</div>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn icon class="mx-auto">
              <v-icon>mdi-heart-multiple</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import charts from "@/components/base/charts";

export default {
  props: {
    source: String
  },
  components: {
    chart: charts
  },
  data: () => ({
    cards: [
      { title: "This a card 1", content: "Home card 1", flex: 6 },
      { title: "This a card 2", content: "Home card 2", flex: 6 },
      { title: "This a card 3", content: "Home card 3", flex: 6 },
      { title: "This a card 4", content: "Home card 4", flex: 6 }
    ],
    desserts: [],
    headers: [
      { text: "Word", value: "word" },
      { text: "Count", value: "count" }
    ],
    loading: true
  }),
  methods: {
    getUserword() {
      this.$axios
        .get("/user/word", {})
        .then(response => {
          // var obj = JSON.parse(response.data);
          if (this.desserts) {
            this.desserts = response.data;
            this.loading = false;
          }
        })
        .catch(error => {
          console.log(error.response);
        });
    }
  },
  created() {
    // this.getUserword();
  }
};
</script>

<style scoped>
#user_word {
  height: 50rem;
  width: 20rem;
}
</style>
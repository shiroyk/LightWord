<template>
  <div class="bg" :style="bgimg">
    <v-row align="content-space-around" justify="center" style="height:90%" no-gutters>
      <v-col class="text-center" cols="12">
        <h1 style="color:rgb(255, 255, 255, 0.7)">
          Light
          <br v-show="!$vuetify.breakpoint.xs" />
          Word
        </h1>
      </v-col>
      <v-spacer></v-spacer>
      <v-col style="min-width:200px" align-self="center" cols="12" sm="3">
        <v-img class="mx-auto" max-width="320" :aspect-ratio="16/9" contain :src="catimg"></v-img>
      </v-col>
      <v-col
        v-show="!$vuetify.breakpoint.xs"
        align-self="center"
        style="min-height: 100px;max-width: 1px;border:1px solid rgb(255, 255, 255, 0.8)"
        sm="auto"
      ></v-col>
      <v-col style="min-width:200px" align-self="center" class="text-center" cols="12" sm="3">
        <p class="title font-weight-light white--text">To remember your cards</p>
        <v-btn v-if="token" dark icon to="/home">
          <v-icon>mdi-home</v-icon>
        </v-btn>
        <v-btn v-else dark rounded text color="white" @click="logindialog = !logindialog">Login</v-btn>
      </v-col>
      <v-col cols="12">
        <v-card
          elevation="24"
          height="13rem"
          width="23rem"
          class="mx-auto"
          style="background-color:rgb(255, 255, 255, 0.6)"
        >
          <v-carousel
            light
            cycle
            :continuous="true"
            :show-arrows="false"
            hide-delimiter-background
            delimiter-icon="mdi-minus"
            height="13rem"
          >
            <v-carousel-item v-for="(card, i) in cards" :key="i">
              <v-card-text>
                <div class="black--text d-flex justify-space-between">
                  {{card.title}}
                  <v-btn x-small icon>
                    <v-icon>mdi-help-circle</v-icon>
                  </v-btn>
                </div>
                <p
                  class="py-3 display-1 black--text font-weight-thin p-5 text-center"
                >{{card.content}}</p>
                <p class="black--text body-2">{{card.sentence}}</p>
              </v-card-text>
            </v-carousel-item>
          </v-carousel>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-model="logindialog" width="25rem" content-class="round">
      <v-card>
        <v-tabs color="secondary" left>
          <v-tab>Login</v-tab>
          <v-tab>Sign up</v-tab>
          <v-tab>Reset</v-tab>
          <v-btn
            color="deep-orange lighten-1"
            icon
            dark
            small
            absolute
            top
            right
            @click="logindialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-tab-item :transition="false" :reverse-transition="false">
            <login></login>
          </v-tab-item>
          <v-tab-item :transition="false" :reverse-transition="false">
            <register></register>
          </v-tab-item>
          <v-tab-item :transition="false" :reverse-transition="false">
            <login></login>
          </v-tab-item>
        </v-tabs>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Login from "@/components/auth/login";
import Register from "@/components/auth/register";
export default {
  props: {
    source: String
  },
  components: {
    login: Login,
    register: Register
  },
  computed: {
    ...mapState({
      token: state => state.auth.token
    })
  },
  data: () => ({
    logindialog: false,
    cards: [
      {
        title: "Word of the Today",
        content: "acquire",
        sentence: "Living alone is an acquired taste."
      },
      {
        title: "Word of the Today",
        content: "dappled",
        sentence: "The path was dappled with sunlight."
      },
      {
        title: "Word of the Today",
        content: "hypothetical",
        sentence: "A purely hypothetical question."
      },
      {
        title: "Word of the Today",
        content: "incompatible",
        sentence: "We were totally incompatible."
      },
      {
        title: "Word of the Today",
        content: "incompatible",
        sentence: "We were totally incompatible."
      }
    ],
    catimg: require("../assets/cat.png"),
    bgimg: {
      backgroundImage: "url(" + require("../assets/bg.jpg") + ")"
    }
  })
};
</script>

<style>
.round {
  border-radius: 15px !important;
  overflow: hidden;
}
.bg {
  background-size: cover;
  background-position: center;
  position: relative;
  width: 100%;
  height: 100%;
  min-width: 100%;
  min-height: 100%;
  overflow: hidden;
  -ms-overflow-style: none;
}
</style>
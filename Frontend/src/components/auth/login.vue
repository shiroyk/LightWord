<template>
  <v-form ref="form" v-model="valid" lazy-validation>
    <div style="padding: 16px 16px 0px 16px">
      <v-text-field
        v-model="username"
        label="Username or email"
        :rules="nm_Rules"
        required
        outlined
        rounded
        dense
        autocomplete
        :error-messages="messages"
        @focus="clearMessages"
        v-on:input="clearMessages"
      ></v-text-field>
      <v-text-field
        v-model="password"
        :rules="passRules"
        :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
        :type="show ? 'text' : 'password'"
        label="Password"
        required
        outlined
        rounded
        dense
        autocomplete
        @click:append="show = !show"
      ></v-text-field>
    </div>
    <v-btn :disabled="!valid" tile block color="success" @click="login">Login</v-btn>
  </v-form>
</template>

<script>
import { mapState } from "vuex"
export default {
  data: () => ({
    valid: true,
    show: false,
    username: "",
    nm_Rules: [v => !!v || "Usuername or email is required"],
    password: "",
    passRules: [
      v => !!v || "Password is required",
      v => (v && v.length >= 6) || "Password must have 6+ characters",
      v => (v && v.length <= 16) || "Password must be less than 16 characters"
    ]
  }),
  computed: {
    ...mapState({
      messages: state => state.auth.login.messages
    })
  },
  methods: {
    login() {
      let username = this.username 
      let password = this.password
      this.$store.dispatch('login', { username, password })
      .then(() => { this.$router.push('/home') })
      .catch(error => { console.log(error) })
    },
    clearMessages() {
      this.$store.commit("loginMessage", []);
    }
  }
};
</script>
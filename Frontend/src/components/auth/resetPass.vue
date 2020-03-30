<template>
  <v-form ref="form" v-model="valid" lazy-validation>
    <div style="padding: 16px 16px 0px 16px">
      <v-text-field
        v-model="usermail"
        :rules="emailRules"
        label="Email Address"
        required
        outlined
        rounded
        dense
        :error="messages.length > 0"
        @focus="clearMessages"
        v-on:input="clearMessages"
      >
        <template v-slot:append-outer>
          <v-btn
            :disabled="usermail && disableCode"
            :loading="disableCode"
            icon
            small
            @click="sendCode"
          >
            <v-icon>mdi-send</v-icon>
            <template v-slot:loader>
              <span>{{countTime + 's'}}</span>
            </template>
          </v-btn>
        </template>
      </v-text-field>
      <v-text-field
        v-model="code"
        :counter="6"
        :rules="codeRules"
        label="Vertify code"
        required
        outlined
        rounded
        dense
        :error="messages.length > 0"
        @focus="clearMessages"
        v-on:input="clearMessages"
      ></v-text-field>
      <v-text-field
        v-model="password"
        :rules="passRules"
        :counter="16"
        :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
        :type="show ? 'text' : 'password'"
        label="Password"
        required
        outlined
        rounded
        dense
        :error-messages="messages"
        @focus="clearMessages"
        v-on:input="clearMessages"
      ></v-text-field>
    </div>
    <v-btn :disabled="!valid" tile block color="success" @click="reset">Reset Password</v-btn>
  </v-form>
</template>

<script>
export default {
  data: () => ({
    valid: true,
    show: false,
    disableCode: false,
    countTime: 60,
    messages: [],
    usermail: "",
    emailRules: [
      v => !!v || "Email is required",
      v =>
        /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/.test(v) ||
        "E-mail must be valid"
    ],
    password: "",
    passRules: [
      v => !!v || "Password is required",
      v => (v && v.length >= 6) || "Password must have 6+ characters",
      v => (v && v.length <= 16) || "Password must be less than 16 characters"
    ],
    code: "",
    codeRules: [
      v => !!v || "Verifiy code is required",
      v => (v && v.length == 6) || "Verifiy code must have 6 characters"
    ]
  }),
  methods: {
    reset() {
      this.$axios
        .post("/user/reset", {
          usermail: this.usermail,
          password: this.password,
          code: this.code
        })
        .then(response => {
          if (response.status == 200) {
            this.$dialog("Successful", {
              message: "<p class='text-center'>重置密码成功</p>",
              color: "success",
              timeout: 0
            });
          }
        })
        .catch(error => {
          let errorStatus = error.response.status
          if (errorStatus == 400 || errorStatus == 429) {
            this.messages = error.response.data.message;
          }
        });
    },
    clearMessages() {
      this.messages = [];
    },
    sendCode() {
      if (!this.disableCode) {
        this.$axios
          .get(`/user/verification/${this.usermail}`, {})
          .then(response => {
            console.log(response);
            this.disableCode = true;
            let countDown = window.setInterval(() => {
              this.countTime--;
              if (this.countTime < 0) {
                window.clearInterval(countDown);
                this.countTime = 60;
                this.disableCode = false;
              }
            }, 1000);
          })
          .catch(error => {
            let errorStatus = error.response.status
            if (errorStatus == 400 || errorStatus == 429) {
              this.messages = error.response.data.message;
            }
          });
      }
    }
  }
};
</script>
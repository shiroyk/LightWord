<template>
  <v-container>
      <v-card class="account mx-auto" :loading="isLoading">
      <v-tabs centered :vertical="$vuetify.breakpoint.smAndUp" class="tab-start">
        <v-tab>
          <v-icon left>mdi-settings</v-icon>
          setting
        </v-tab>
        <v-tab>
          <v-icon left>mdi-account</v-icon>
          account
        </v-tab>

        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <v-row
                align="center"
                justify="center"
              >
                <v-col cols="10">
                  <v-autocomplete
                    v-model="t_v"
                    :items="types"
                    hide-no-data
                    hide-details
                    dense
                    outlined
                    label="Types"
                  ></v-autocomplete>
                </v-col>
                <v-col cols="10">
                  <v-autocomplete
                    v-model="p_v"
                    :items="pronounce"
                    hide-details
                    dense
                    outlined
                    label="Pronounce"
                  ></v-autocomplete>
                </v-col> 
                <v-col cols="10">
                  <div class="d-flex" style="justify-content:flex-end;">
                    <v-btn text small @click="isLoading = true;putConfig()">Save</v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-tab-item>
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <p>
                Account setting         
              </p>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs>
    </v-card>
  </v-container>
</template>

<script>
export default {
  props: {
    source: String
  },
  data: () => ({
    types: [],
    typesDict: {},
    t_v: null,
    e_v: null,
    p_v: null,
    isLoading: false,
    pronounce: ["Birtish", "Ameracian"],
  }),
  methods: {
    getConfig() {
      this.isLoading = true
      this.$axios.all([
          this.$axios.get('/resource/type'), 
          this.$axios.get('/user/config')
      ]).then(([vtypes, config]) => {
        var t = vtypes.data;
        var c = config.data;
        for(var i = 0, len = t.length; i < len; i++){
              const vocabtype = t[i].vocabtype
              this.typesDict[vocabtype] = t[i].id
              this.types.push(vocabtype)
          }
        this.t_v = this.types[c.vtype - 1]
        this.p_v = this.pronounce[c.pronounce]
      });
    },
    putConfig() {
      let putData = {
        vtype: this.typesDict[this.t_v],
        pronounce: this.pronounce.indexOf(this.p_v)
      }
      this.$axios.put('/user/config',putData
      ).then((response)=>{
        if (response.status==200) {
          console.log("Ok")
        }
      }).catch((error)=>{
          console.log(error.response)
      })
    },
  },
  watch: {
    isLoading (val) {
      if (val) {
        setTimeout(() => (this.isLoading = false), 1000)
      }
    },
  },
  created() {
    this.getConfig()
  }
}
</script>

<style scoped>
.account {
  margin: 1rem;
  max-width: 35rem;
}
div.tab-start [role="tab"] {
  justify-content: flex-start;
}
</style>
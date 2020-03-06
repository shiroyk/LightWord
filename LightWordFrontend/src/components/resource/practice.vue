<template>
  <div class="card-container">
    <div class="mx-auto d-flex justify-center">
      <div
        class="d-flex align-center left-arrow"
        :class="{'card-slide-btn-xs': $vuetify.breakpoint.xs, 'card-slide-btn': $vuetify.breakpoint.smAndUp, 'hidden': leftbtn}"
        @click="prevCard"
      >
        <v-icon color="light-blue accent-4" :large="$vuetify.breakpoint.smAndUp">mdi-chevron-left</v-icon>
      </div>
      <v-card :loading="isLoading" class="card d-flex flex-column flex-auto">
        <div class="d-flex justify-space-between p-1">
          <v-btn icon height="25" width="25" @click="overlay = !overlay">
            <v-progress-circular
              :indeterminate="isLoading"
              :value="(currentCard+1)*10"
              size="25"
              width="5"
              :color="status ? 'green accent-4' : 'yellow accent-4'"
            ></v-progress-circular>
          </v-btn>
          <v-overlay absolute :value="overlay" opacity="0.6">
            <div class="mx-auto">
              <p>是否已掌握该单词？</p>
              <div class="d-flex justify-space-between mx-auto" style="width:6rem">
                <v-btn icon @click="overlay = !overlay;graspCard()">
                  是
                </v-btn>
                <v-btn icon @click="overlay = !overlay">
                  否
                </v-btn>
              </div>
            </div>
          </v-overlay>

          <span class="mb-4">{{currentWord}}</span>
          <span>{{additional}}</span>
        </div>
        <div
          class="d-flex flex-column flex-auto"
          :style="{'font-size': textSize(lsentense+rsentense)}"
          :class="{'card-body-xs': $vuetify.breakpoint.xs, 'card-body': $vuetify.breakpoint.smAndUp}"
        >
          <div class="flex-auto">
            <span>{{lsentense}}</span>
            <span
              class="input-container"
              :class="{'input-container-correct': correct, 'input-container-wrong': wrong}"
            >
              <transition name="fade">
                <span v-if="showWord" class="fade current-word">{{currentWord}}</span>
              </transition>
              <span class="hidden-word">
                <span v-for="(w,i) in currentWord" :key="i">{{w}}</span>
              </span>
              <input
                ref="inputword"
                id="inputword"
                class="input-field"
                type="text"
                :style="{'color': correct ? '#81C784':'' }"
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                oncontextmenu="return false"
                spellcheck="false"
                maxlength="20"
                :disabled="inputDisabled"
                @click="showWord = false"
                v-on:input="showWord = false"
                @keyup.enter="nextCard"
              />
            </span>
            <span>{{rsentense}}</span>
          </div>
          <p class="sentence-translation">{{translation}}</p>
        </div>
        <div class="d-flex justify-space-between p-1">
          <span>{{meaning}}</span>
          <v-btn height="25" width="25" icon @click="volume=!volume">
            <v-icon>{{volume ? "mdi-volume-high":"mdi-volume-off"}}</v-icon>
          </v-btn>
        </div>
      </v-card>

      <div
        class="d-flex align-center right-arrow"
        :class="{'card-slide-btn-xs': $vuetify.breakpoint.xs, 'card-slide-btn': $vuetify.breakpoint.smAndUp}"
        @click="nextCard"
      >
        <v-icon
          color="light-blue accent-4"
          :large="$vuetify.breakpoint.smAndUp"
          v-show="rightbtn"
        >mdi-chevron-right</v-icon>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    source: String
  },
  data: () => ({
    overlay: false,
    volume: true,
    showWord: false,
    correct: false,
    wrong: false,
    array: [],
    wid: 0,
    tid: 0,
    card: 0,
    currentCard: 0,
    status: "",
    lsentense: "",
    rsentense: "",
    meaning: "",
    inflection: "",
    additional: "",
    pronounce: "",
    currentWord: "",
    translation: "",
    rightbtn: true,
    leftbtn: true,
    isLoading: false,
    inputDisabled: false
  }),
  methods: {
    getResource() {
      this.isLoading = true;
      this.$axios
        .get("/resource", {})
        .then(response => {
          this.array = response.data;
          this.readData(this.array[this.card]);
          this.isLoading = false;
          this.$nextTick(() => {
            this.$refs.inputword.focus();
          });
        })
        .catch(error => {
          console.log(error);
        });
    },
    putData(status) {
      this.$axios
        .put("/resource/practice", {
          word: this.wid,
          vtype: this.tid,
          status: status
        })
        .then(response => {
          if (response.status == 200) {
            console.log("Ok");
          }
        })
        .catch(error => {
          console.log(error);
        });
    },
    readData(data) {
      if (data.status == "Remember") {
        this.status = true;
      } else {
        this.status = false;
      }
      this.currentWord = data.example.word;

      this.inflection = data.inflection;
      this.lsentense = data.example.split[0];
      this.rsentense = data.example.split[1];
      this.translation = data.example.translation;
      this.meaning = data.meaning;
      this.pronounce = data.pronounce;
      this.additional = data.additional;
      this.wid = data.id;
      this.tid = data.vtype;
    },
    prevCard() {
      if (this.card > 0) {
        this.card -= 1;
        this.readData(this.array[this.card]);
        this.$refs.inputword.value = this.currentWord;
        this.inputDisabled = true;
        if (this.card == 0) {
          this.leftbtn = true;
        }
      }
    },
    playVoice() {
      //暂未添加
      if (this.volume) {
        return new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        return new Promise(resolve => setTimeout(resolve, 1000));
      }
    },
    async nextCard() {
      if (this.currentCard == this.card) {
        this.inputDisabled = false;
        let inputValue = this.$refs.inputword.value.toLowerCase();
        if (
          inputValue == this.currentWord.toLowerCase() ||
          this.inflection.includes(inputValue)
        ) {
          this.putData(1);
          this.correct = true;
          this.$refs.inputword.value = this.currentWord;
          await this.playVoice();
          this.correct = false;

          if (this.card < 9) {
            this.card += 1;
            this.currentCard = this.card;
            this.readData(this.array[this.card]);
            this.$refs.inputword.value = "";
          } else {
            this.card = 0;
            this.currentCard = 0;
            this.getResource();
          }
        } else {
          this.wrong = true;
          this.putData(2);
          this.$refs.inputword.value = "";
          this.showWord = true;
          setTimeout(
            () => ((this.showWord = false), (this.wrong = false)),
            3000
          );
        }
      } else {
        this.card += 1;
        this.readData(this.array[this.card]);
        if (this.currentCard > this.card) {
          this.$refs.inputword.value = this.currentWord;
          this.inputDisabled = true;
        } else {
          this.inputDisabled = false;
          this.$refs.inputword.value = "";
        }
      }
      if (this.currentCard > 0) {
        this.leftbtn = false;
      }
    },
    graspCard() {
      this.putData(3);
      this.card += 1;
      this.currentCard = this.card;
      this.readData(this.array[this.card]);
    },
  },
  created: function() {
    this.getResource();
  },
  mounted() {},
  computed: {
    textSize() {
      return function(value) {
        if (value == "") {
          return "100%";
        } else {
          return 5 / String(value).length + 1.5 + "rem";
        }
      };
    }
  }
};
</script>

<style src="@/assets/practice.css">
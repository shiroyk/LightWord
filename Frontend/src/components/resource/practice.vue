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
              :value="(card + 1) / cardArray.length * 100"
              size="25"
              width="5"
              :color="cardData.status == 'Remember' ? 'green accent-4' : 'yellow accent-4'"
            ></v-progress-circular>
          </v-btn>
          <v-overlay absolute :value="overlay" opacity="0.6">
            <div class="mx-auto">
              <p>是否已掌握该单词？</p>
              <div class="d-flex justify-space-between mx-auto" style="width:8rem">
                <v-btn icon @click="overlay = !overlay;graspCard()">是</v-btn>
                <v-btn icon @click="overlay = !overlay">否</v-btn>
              </div>
            </div>
          </v-overlay>

          <span>{{cardData.additional}}</span>
        </div>
        <div
          class="d-flex flex-column flex-auto"
          :style="{'font-size': 5 / String(cardData.example.sentence).length + 1.5 + 'rem'}"
          :class="{'card-body-xs': $vuetify.breakpoint.xs, 'card-body': $vuetify.breakpoint.smAndUp}"
        >
          <div class="flex-auto">
            <span>{{cardData.example.split[0]}}</span>
            <span
              class="input-container"
              :class="{'input-container-correct': correct, 'input-container-wrong': wrong}"
            >
              <transition name="fade">
                <span v-if="showWord" class="fade current-word">{{cardData.word}}</span>
              </transition>
              <span class="hidden-word">
                <span v-for="(w,i) in cardData.word" :key="i">{{w}}</span>
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
                @click="showWord = wrong = false"
                v-on:input="showWord = wrong = false"
                @keyup.enter="nextFlag && nextCard()"
              />
            </span>
            <span>{{cardData.example.split[1]}}</span>
          </div>
          <p class="sentence-translation">{{cardData.example.translation}}</p>
        </div>
        <div class="d-flex justify-space-between p-1">
          <span>{{cardData.meaning}}</span>
          <v-btn height="25" width="25" icon @click="setVolume">
            <v-icon>{{volume ? "mdi-volume-high":"mdi-volume-off"}}</v-icon>
          </v-btn>
        </div>
      </v-card>

      <div
        class="d-flex align-center right-arrow"
        :class="{'card-slide-btn-xs': $vuetify.breakpoint.xs, 'card-slide-btn': $vuetify.breakpoint.smAndUp}"
        @click="nextFlag && nextCard()"
      >
        <v-icon color="light-blue accent-4" :large="$vuetify.breakpoint.smAndUp">mdi-chevron-right</v-icon>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  props: {
    source: String
  },
  data: () => ({
    overlay: false,
    showWord: false,
    correct: false,
    wrong: false,
    cardArray: [],
    targetDialog: true,
    card: 0,
    currentCard: 0,
    cardData: {
      additional: "",
      example: {
        sentence: "",
        split: ["", ""],
        translation: "",
        word: ""
      },
      id: 0,
      inflection: [],
      meaning: "",
      pronounce: "",
      status: "",
      vtype: 0,
      word: ""
    },
    nextFlag: true,
    wrongFlag: false,
    leftbtn: true,
    isLoading: false,
    inputDisabled: false
  }),
  methods: {
    getTarget() {
      if (this.target != null) return;

      this.$axios
        .get("/user/config", {})
        .then(response => {
          let target = response.data.target;
          this.$store.commit("setTarget", target);
        })
        .catch(error => {
          console.log(error);
        });
    },
    getResource() {
      this.isLoading = true;
      this.$axios
        .get("/resource/exercise", {})
        .then(response => {
          this.cardArray = response.data;
          this.cardData = this.cardArray[this.currentCard];
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
      return new Promise(resolve => {
        this.$axios
          .put("/resource/exercise/status", {
            word: this.cardData.id,
            vtype: this.cardData.vtype,
            status: status
          })
          .then(response => {
            resolve(response.data);
          })
          .catch(error => {
            console.log(error);
          });
      });
    },
    prevCard() {
      if (this.card > 0) {
        this.card -= 1;
        this.cardData = this.cardArray[this.card];
        this.$refs.inputword.value = this.cardData.word;
        this.inputDisabled = true;
      }
    },
    playVoice() {
      if (this.volume) {
        return new Promise((resolve, reject) => {
          var audio = new Audio();
          this.$axios
            .post("/resource/exercise/speech", {
              text: this.cardData.example.sentence
            })
            .then(response => {
              audio.autoplay = true;
              audio.onerror = reject;
              audio.onended = resolve;
              audio.src = "data:audio/mp3;base64," + response.data;
            })
            .catch(error => {
              console.log(error);
            });
        });
      } else {
        return new Promise(resolve => setTimeout(resolve, 1000));
      }
    },
    async nextCard() {
      if (this.currentCard == this.card) {
        this.inputDisabled = false;
        let inputValue = this.$refs.inputword.value.toLowerCase();
        if (
          inputValue == this.cardData.word.toLowerCase() ||
          this.cardData.inflection.includes(inputValue)
        ) {
          // 如果结果正确
          this.nextFlag = false;
          // 防止多次执行
          this.correct = true;
          await this.playVoice().then(() => {
            this.nextFlag = true;
            // 重置执行状态
            this.correct = false;
          });
          this.putData(1).then(data => {
            if (data.added == this.target && this.targetDialog) {
              this.targetDialog = false;
              this.$dialog("Message", {
                message: "<p class='text-center'>今日目标已完成</p>",
                color: "primary",
                timeout: 0
              });
            }
          });
          this.$refs.inputword.value = this.cardData.word;

          this.card += 1;
          this.$refs.inputword.value = "";

          if (this.card < this.cardArray.length) {
            this.currentCard = this.card;
            this.cardData = this.cardArray[this.card];
          } else {
            this.card = 0;
            this.currentCard = 0;
            this.getResource();
          }

          this.wrongFlag = false;
          // 重置传递状态
        } else {
          // 如果结果错误
          this.wrong = true;
          this.showWord = true;
          this.$refs.inputword.value = "";
          if (!this.wrongFlag) {
            this.putData(2).then(() => {
              this.wrongFlag = true;
              // 防止多次传递给后端
              setTimeout(
                () => ((this.showWord = false), (this.wrong = false)),
                3000
              );
            });
          }
        }
      } else {
        // 前后卡片
        this.card += 1;
        this.cardData = this.cardArray[this.card];
        if (this.currentCard > this.card) {
          this.$refs.inputword.value = this.cardData.word;
          this.inputDisabled = true;
        } else {
          this.inputDisabled = false;
          this.$refs.inputword.value = "";
        }
      }
    },
    graspCard() {
      this.putData(3);
      this.card += 1;
      this.currentCard = this.card;
      this.cardData = this.cardArray[this.card];
    },
    setVolume() {
      if (this.volume) {
        this.$store.commit("setVolume", false);
      } else {
        this.$store.commit("setVolume", true);
      }
    }
  },
  created() {
    this.getResource();
  },
  mounted() {
    this.getTarget();
  },
  watch: {
    card(val) {
      if (val > 0) {
        this.leftbtn = false;
      } else {
        this.leftbtn = true;
      }
    }
  },
  computed: {
    ...mapState({
      volume: state => state.practice.volume,
      target: state => state.practice.target
    })
  }
};
</script>

<style src="@/assets/practice.css">
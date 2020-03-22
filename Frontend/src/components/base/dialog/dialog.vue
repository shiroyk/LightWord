<template>
  <v-dialog v-model="messageDialog" persistent :width="width">
    <v-card :color="color" dark>
      <v-card-title class="text-center" v-if="title.length > 0 || $slots.title">
        <slot name="title">
          <span>{{ title }}</span>
        </slot>
        <v-btn v-if="showClose" icon dark small absolute top right @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <div v-if="message.length > 0 || $slots.message">
          <slot name="message">
            <div v-html="message" />
          </slot>
        </div>
        <v-progress-linear
          v-if="progress.length && progress == 'linear'"
          indeterminate
          color="white"
        ></v-progress-linear>
        <v-progress-circular v-else-if="progress.length" indeterminate color="white"></v-progress-circular>
      </v-card-text>
      <v-card-actions v-if="$slots.button">
        <div class="mx-auto">
          <slot name="button"></slot>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    messageDialog: {
      type: Boolean,
      default: false
    },
    width: {
      type: Number,
      default: 300
    },
    heigh: Number,
    message: {
      type: String,
      default: ""
    },
    title: {
      type: String,
      default: "Loading..."
    },
    color: String,
    showClose: {
      type: Boolean,
      default: true
    },
    progress: {
      type: String,
      default: ""
    },
    icon: {
      type: String,
      default: ""
    },
    timeout: {
      type: Number,
      default: 2000
    },
    push: {
      type: String,
      default: ""
    }
  },
  data: () => ({}),
  watch: {
    messageDialog(vlaue) {
      if (vlaue) {
        this.messageDialog = vlaue;
        if (this.timeout) {
          return new Promise(resolve => {
            resolve(setTimeout(() => this.closeDialog(), this.timeout));
          });
        }
      }
    }
  },
  mounted() {},
  methods: {
    closeDialog() {
      this.messageDialog = false;
      this.$emit("dialog", false);
    }
  }
};
</script>
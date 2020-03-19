<template>
  <div>
    <div v-if="$vuetify.breakpoint.xs">
      <div id="piechart" v-show="chartShow" v-resize="chartResize" class="xsCharts"></div>
      <div id="linechart" v-show="!chartShow" v-resize="chartResize" class="xsCharts"></div>
      <v-btn color="primary" dark absolute right top icon @click="chartType">
        <v-icon>mdi-cached</v-icon>
      </v-btn>
    </div>
    <div v-else class="d-flex justify-space-between mx-auto" style="max-width: 60rem">
      <div id="piechart" class="d-flex xsupCharts" v-resize="chartResize"></div>
      <div id="linechart" class="d-flex xsupCharts" v-resize="chartResize"></div>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    chartShow: true,
    dateArray: [],
    pieArray: [],
    correctArray: [],
    wrongArray: [],
    noDataOption: {
      title: {
        text: "No Data",
        textStyle: {
          color: "#757575",
          fontSize: 20
        },
        left: "center",
        top: "center"
      },
    },
    pieOption: {
      //piechart
      title: {
        text: "pie",
        textStyle: {
          color: "#757575"
        },
        left: "center"
      },
      tooltip: {
        trigger: "item",
        formatter: "{b} : {c} ({d}%)"
      },
      legend: {
        left: "center",
        top: "bottom",
        data: []
      },
      series: [
        {
          type: "pie",
          radius: [30, 110],
          roseType: "area",
          data: []
        }
      ]
    },
    lineOption: {
      //linechart
      title: {
        text: "line",
        left: "center",
        textStyle: {
          color: "#757575"
        },
      },
      color: ["#5793f3", "#d14a61"],
      tooltip: {
        trigger: "axis"
      },
      legend: {
        data: ["Correct", "Wrong"]
      },
      xAxis: {
        type: "category",
        data: [],
        axisLabel: {
          show: true,
          textStyle: {
            color: "#757575"
          }
        }
      },
      yAxis: {
        type: "value",
        axisLabel: {
          show: true,
          textStyle: {
            color: "#757575"
          }
        }
      },
      series: [
        {
          name: "Correct",
          type: "line",
          smooth: true,
          data: []
        },
        {
          name: "Wrong",
          type: "line",
          smooth: true,
          data: []
        }
      ]
    }
  }),
  methods: {
    getStatistc() {
      this.isLoading = true;
      this.$axios
        .get("/user/statistic?days=10", {})
        .then(response => {
          const data = response.data;
          if (data.length != 0) {
              for (var i = 0, len = data.length; i < len; i++) {
              let day = data[i].day;
              this.dateArray.push(day);
              this.pieArray.push({ value: data[i].count, name: day });
              this.correctArray.push(data[i].correct);
              this.wrongArray.push(data[i].wrong);
            }
            this.pieOption.legend.data = this.dateArray;
            this.pieOption.series[0].data = this.pieArray;
            this.lineOption.xAxis.data = this.dateArray;
            this.lineOption.series[0].data = this.correctArray;
            this.lineOption.series[1].data = this.wrongArray;
            
          } else {
            this.pieOption = this.noDataOption
            this.lineOption = this.noDataOption
          }
          this.pieChart();
          this.lineChart();
        })
        .catch(error => {
          console.log(error);
        });
    },
    chartResize() {
      setTimeout(
        () => (this.pieChart().resize(), this.lineChart().resize()),
        20
      );
    },
    pieChart() {
      let myChart = this.$echarts.init(document.getElementById("piechart"));
      myChart.setOption(this.pieOption);
      return myChart;
    },
    lineChart() {
      let myChart = this.$echarts.init(document.getElementById("linechart"));
      myChart.setOption(this.lineOption);
      return myChart;
    },
    chartType() {
      this.chartShow = !this.chartShow;
      this.chartResize();
    }
  },
  mounted() {
    this.getStatistc();
  }
};
</script>

<style scoped>
.xsCharts {
  min-width: 100%;
  height: 400px;
}
.xsupCharts {
  width: 100%;
  height: 400px;
}
</style>
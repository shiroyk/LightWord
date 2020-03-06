const CompressionWebpackPlugin = require('compression-webpack-plugin');
      
module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  configureWebpack: {
    plugins:[
      new CompressionWebpackPlugin({
        algorithm: 'gzip',
        test: /\.js$|\.html$|\.json$|\.css/,
        threshold: 10240,
        minRatio: 0.8
       })
    ],
    devtool: 'source-map'
  }
}
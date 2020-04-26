<template>
<div class='main-div-container'>
  <el-card class="box-card" shadow="never">
    <div slot="header" class="clearfix">
    <span style="float:left">端口扫描选项</span>
    <!-- <el-button style="float: right; padding: 3px 0" type="text">操作按钮</el-button> -->
    </div>
    <el-form>
        <el-form-item>
        <span>masscan路径: </span>
        <el-input class="class-setup" v-model="masscanPath" size="mini"></el-input>
        <el-button size="mini" type="primary" @click="updatePath">更改</el-button>
        </el-form-item>
        <el-form-item>
        <span>masscan速率</span>
        <el-input class="class-setup" v-model="masscanRate" size="mini"></el-input>
        <el-button size="mini" type="primary" @click="updatePath">更改</el-button>
        </el-form-item>
    </el-form>
  </el-card>
</div>

</template>>

<script>
export default{
  data () {
    return {
      masscanPath: '/usr/local/bin/masscan',
      masscanRate: 1800
    }
  },
  methods: {
    updatePath () {}
  }
}

</script>
<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
    .class-setup {
        margin-right: 10px;
        width: 233px;
        margin-top: 15px;
        margin-left: 10px;
        vertical-align: bottom;
    }
    .class-setup .el-input__inner {
        height: 30px;
    }
   .text {
    font-size: 14px;
  }

  .item {
    margin-bottom: 18px;
  }

  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }

  .box-card {
    width: 480px;
  }
</style>

<template>
    <div class="navigation">
        <el-menu
                background-color="#24292e"

                active-text-color="#409EFF"
                text-color="rgba(255, 255, 255, 0.75)"
                :default-active="activeIndex"
                router
                mode="horizontal">
            <!-- <el-menu-item index="/" >
                <img src="./../assets/github.svg" style="font-size: 20px;width: 3em;height: 1.0em;" alt="">
                漏洞管理
                 text-color="rgba(255, 255, 255, 0.75)"
                 #ffd04b
            </el-menu-item> -->
            <!-- <el-menu-item index="/" disabled="">
                概览
            </el-menu-item> -->
            <el-menu-item index="/">
            <!-- <img src="./../assets/robot.svg" style="font-size: 20px;width: 3em;height: 1.0em;" alt=""> -->
            <i class="iconfont icon-loudongsaomiao"></i>
                任务管理
            </el-menu-item>
            <el-menu-item index="/group" >
             <i class="iconfont icon-zhuji"></i>
                主机分组

            </el-menu-item>
            <el-menu-item index="/vuln" >
            <i class="iconfont icon-loudong1"></i>
                漏洞管理
            </el-menu-item>
            <el-menu-item index="/devices">
            <i class="iconfont icon-zichanguanli"></i>
                资产管理
            </el-menu-item>

            <el-menu-item index="/poc">
            <i class="iconfont icon-wuqiku"></i>
                POCS
            </el-menu-item>

            <el-menu-item index="/settings" disabled>
            <i class="iconfont icon-shezhi"></i>
                设置
            </el-menu-item>
        </el-menu>
    </div>
</template>

<script>
export default {
  data () {
    return {}
  },
  computed: {
    activeIndex () {
      return this.$route.name
    }
  },
  mounted: function () {
    this.$nextTick(function () {
    })
  }
}
</script>

<style>
@import '../styles/icons/iconfont.css';
    .el-menu-item a {
        text-decoration: none;
        display: block;
    }
</style>

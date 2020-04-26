<template>
<div>

  <NavMenu/>
          <!-- <div class="breadcrumb" v-if="$route.path!=='/'">
            <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{$route.meta.name}}</el-breadcrumb-item>
            </el-breadcrumb>
        </div> -->
  <div id="app">
    <!-- <img src="./assets/logo.png"> -->
    <router-view/>
  </div>
</div>
</template>

<script>
const NavMenu = () => import('@/components/NavMent')

export default {
  name: 'App',
  components: {
    NavMenu
  }
}
</script>

<style>
#app {
 font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 1px;
}
.breadcrumb {
        padding: 20px 20px 20px 20px;
        background-color: #fff;
        /*margin-bottom: 5px;*/
    }
a {
  text-decoration: none;
}
</style>

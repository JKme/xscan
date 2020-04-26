import axios from 'axios'
import { Message, Loading } from 'element-ui'

// 允许携带cookie
// axios.defaults.withCredentials = true
let loading
// 定义loading变量
export function startLoading () {
  // 使用Element loading-start 方法
  loading = Loading.service({
    lock: true,
    text: '加载中……',
    background: 'rgba(0, 0, 0, 0)' })
}
export function endLoading () {
  // 使用Element loading-close 方法
  loading.close()
}

// session状态提示信息方法
export function SessionStatusMessage (msg) {
  console.log(msg)
  Message({
    message: '接口无响应，请重新刷新...',
    type: 'error',
    duration: 5 * 1000
  })
}
// create an axios instance
const service = axios.create({
  baseURL: process.env.BASE_API, // api 的 base_url
  timeout: 20000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // console.log(config)
    // console.log(config.url)
    if (config.method === 'post') {
      if (config.specialType !== undefined) {
        config.headers['Content-Type'] = config.specialType
      } else {
        config.headers['Content-Type'] = 'application/json;charset=UTF-8'
      }
    }
    if (config.baseURL !== undefined) {
      const servers = process.env.servers
      for (const key of Object.keys(servers)) {
        if (key === config.baseURL) {
          // 配置了自定义url的，就获取url
          // console.log(config.url)
          console.log(servers[key])
          config.url = servers[key] + config.url

          // config.url = servers[key]
        }
        // config.url = servers[key]
      }
    }
    // startLoading()
    return config
  },
  error => {
    // Do something with request error
    endLoading()
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  response => response,
  /**
   * 下面的注释为通过在response里，自定义code来标示请求状态
   * 当code返回如下情况则说明权限有问题，登出并返回到登录页
   * 如想通过 xmlhttprequest 来状态码标识 逻辑可写在下面error中
   * 以下代码均为样例，请结合自生需求加以修改，若不需要，则可删除
   */
  // response => {
  //   endLoading()
  // const res = response.data
  // 未登录
  // if (res.code === 10001003 && ('data' in res)) {
  //   window.location.href = res.data
  //   // return response
  //   // 未登录不影响原来的编辑
  //   // window.open(res.data, '_blank')
  // } else {
  //   return response
  // }
  // },
  error => {
    endLoading()
    console.log('err：' + error) // for debug
    // 请求失败、错误处理回调
    if (error.code === 'ECONNABORTED' && error.message.indexOf('timeout') !== -1) {
      SessionStatusMessage(error.message)
      return Promise.reject(error)
    } else {
      if (error.message !== '路由跳转取消请求') {
        const e = { ...error }
        // console.log(e.response)
        Message({
          dangerouslyUseHTMLString: true,
          message: 'status: ' + e.response.data.status + '<br>' +
           'error: ' + e.response.data.error + '<br>' +
           'exception: <strong>' + e.response.data.exception + '</strong><br>' +
           'message: ' + e.response.data.message + '<br>' +
           'path: ' + e.response.data.path + '<br>',
          type: 'error',
          duration: 5 * 1000
        })
      } else {
        return new Promise(() => {})
      }
      return Promise.reject(error)
    }
  }
)

export default service

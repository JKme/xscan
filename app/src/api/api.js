import request from '@/api/baseApi'

export function dashboard () {
  return request({
    url: '/api/dashboard/detail',
    method: 'get',
    baseURL: 'backend'
  })
}

export function vulQuery (query) {
  return request({
    url: '/api/dashboard/query',
    method: 'post',
    data: query,
    baseURL: 'backend'
  })
}

export function getTypes () {
  return request({
    url: '/api/dashboard/getvultypes',
    method: 'get',
    baseURL: 'backend'
  })
}

export function testPostParams (params) {
  return request({
    url: '/post',
    method: 'post',
    params: params
  })
}

export function pocQuery (query) {
  return request({
    url: '/api/poc/query',
    method: 'post',
    data: query,
    baseURL: 'backend'
  })
}

export function initPocQuery () {
  return request({
    url: '/api/poc/query',
    method: 'get',
    baseURL: 'backend'
  })
}

export function addTask (params) {
  return request({
    url: '/api/add/task',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function queryTask (params) {
  return request({
    url: '/api/query/task',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function queryTaskId (params) {
  return request({
    url: '/api/query/taskDetail',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function queryTaskTargets (params) {
  return request({
    url: '/api/query/QueryTaskTarget',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function queryDevices (params) {
  return request({
    url: '/api/query/devices',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function queryvul (params) {
  return request({
    url: '/api/query/vul',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function replayTaskApi (params) {
  return request({
    url: '/api/replay/task',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function TagAdd (params) {
  return request({
    url: '/api/settings/tag',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function TagFetch (params) {
  return request({
    url: '/api/settings/tag',
    method: 'get',
    baseURL: 'backend'
  })
}

export function queryTagTarget (params) {
  return request({
    url: '/api/query/QueryTagTarget',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function TagDel (params) {
  return request({
    url: '/api/settings/tag',
    method: 'delete',
    data: params,
    baseURL: 'backend'
  })
}

export function queryTagDetail (params) {
  return request({
    url: '/api/query/tagDetail',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function delTask (params) {
  return request({
    url: '/api/del/task',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function addVulDesc (params) {
  return request({
    url: '/api/add/addVulDesc',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function addVulBlack (params) {
  return request({
    url: '/api/add/addVulBlack',
    method: 'post',
    data: params,
    baseURL: 'backend'
  })
}

export function test (params) {
  return request({
    url: '/test',
    method: 'post',
    data: params,
    baseURL: 'urltest'
  })
}

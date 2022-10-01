import axios from 'axios'
import { url, port } from '@/assets/js/set.js'
import {get_Storage} from '@/assets/js/often.js'

export function reg(data){
    return axios.post(`${url()}${port()}/v1/users/`,data)
}

export function login(data){
    return axios.post(`${url()}${port()}/v1/users/login`,data)
}

export function info(token){
    let cookie = get_Storage('cookie')

    return axios.get(`${url()}${port()}/v1/users/`,{
        headers:{
            "Cookie": cookie,
            "AUTHORIZATION":token
        }
    })
}

export function info_change(data,token){
    return axios.put(`${url()}${port()}/v1/users/`,data,{
        headers:{
            "AUTHORIZATION":token
        }
    })
}

export function avatar_change(formData,token){
    return axios.post(`${url()}${port()}/v1/users/avatar`,formData,{
        headers:{
            "AUTHORIZATION":token
        }
    })
}

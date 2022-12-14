import axios from 'axios'
import { url, port } from '@/assets/js/set.js'


// //載入頁面-瀏覽商品 
export function pbrowser(pattern,browser,page,mode,keyword,account){
	return axios.get(`${url()}${port()}/v1/products/${pattern}/${browser}/${page}/${mode}/${keyword}/${account}`)
}
/* summary */

//修改商品資料
export function psadust(data,account){
	return axios.put(`${url()}${port()}/v1/products/${account}`,data)
}


/* history */

//新增商品
export function padd(data,account){
	return axios.post(`${url()}${port()}/v1/products/${account}`,data)
}

//銷貨商品
export function psale(data,account){
	return axios.post(`${url()}${port()}/v1/managers/${account}`,data)
}
//修改商品資料_history
export function padust(mid,data,account){
	return axios.put(`${url()}${port()}/v1/managers/${mid}/${account}`,data)
}

//刪除商品
export function pdelete(mid,account){
    return axios.delete(`${url()}${port()}/v1/managers/${mid}/${account}`)
}
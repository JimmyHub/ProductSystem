// import { url } from '@/assets/js/set.js'

//localstorage 設置
export function set_Storage(item,value){
    window.localStorage.setItem(item,value)
}
export function get_Storage(item){
    return window.localStorage.getItem(item)
}
export function del_Storage(item){
    window.localStorage.removeItem(item)
}

//sessionstorage設置
export function set_Session(item,value){
    window.sessionStorage.setItem(item,value)
}
export function get_Session(item){
    return window.sessionStorage.getItem(item)
}
export function del_Session(item){
    window.sessionStorage.removeItem(item)
}

//搜尋
//頁面不在就轉跳 如果頁面再就直接改內容 //搬回去放
export function search(){
    let keyword = this.keyword.replace(/\s*/g,"").replace(/\//g,'')
    let mode = this.selected
    if(mode){
        if(keyword){
            set_Session('keyword',keyword)
            set_Session('mode',mode)
            set_Session('pattern','search')
            location.reload()
        }else{
            alert('請輸入關鍵字')
        }
    }else{
        alert('請選擇模式')
    }


}

//返回首頁
export function go_home(){
    window.sessionStorage.clear()
    location.reload()
}


//前往商品詳細內容
export function product_detail(pid){
    set_Storage('keyword',pid)
    set_Storage('pattern','search')
    let num=0
    //從localStorage取道的值為str, 要轉換成陣列
    let record_key = get_Storage('list_key').split(',')
    for(var zr=0;zr<record_key.length;zr++){
        if(record_key[zr] == pid){
            num+=1
        }
    }
    if(num == 0){
        //替換 瀏覽紀錄的商品id
        record_key[0]=record_key[1]
        record_key[1]=record_key[2]
        record_key[2]=pid
        //替換完 更新頁面中的list_key
        set_Storage('list_key',record_key)

        /*for(var n=0;n<record_key.length;n++){
            if(n==2){
                record_key[n]=pid
            }else{
                record_key[n]=record_key[n+1]
            }
        }*/
    }
}
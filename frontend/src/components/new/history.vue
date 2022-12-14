<template src='@/assets/templates/new/summary.html'></template>
<style scoped src='@/assets/css/new/summary.css'></style>
<style scoped src='@/assets/css/common/common_in.css'></style>

<script type="text/javascript">
    import {go_home, search, set_Session, get_Session, del_Session} from'@/assets/js/often.js'     
    import {pbrowser, padd, psale, padust, pdelete} from '@/api/new.js'
    export default{
        name:'order',
        data(){
            return{
                isAll: false,
                isID: -1,
                isInOut:'',
                isAction:'Nothing',
                selected:'',
                keyword:'',
                kind:'',
                type_no:'',
                total:'',
                in_time:'',
                out_time:'',
                in_price:0,
                out_price:0,
                pdatas:[],
                in_total:0,
                out_total:0,
                pcounts:[],
                d_list:[],
            }
        },
        methods:{
            //常見功能
            go_home, search,
            changePage(page){
                console.log(page)
                set_Session('page', page)
                location.reload()
            },
            changeBrowser(browser){
                set_Session('browser',browser)
                location.reload()
            },
            in_show(){
               if(!this.isInOut){
                  this.isInOut = true
                  set_Session('account','in_database')

                  location.reload()
               }
            },
            out_show(){
               if(this.isInOut){
                  this.isInOut = false
                  set_Session('account','out_database')
                  location.reload()
               }
            },
            act_action(action, index){
                if(this.isAction == 'Nothing'){
                    let date = new Date()
                    let y = date.getFullYear()
                    let Mo = date.getMonth()+1
                    Mo = Mo < 10 ? ('0' + Mo) : Mo
                    let d = date.getDate()
                    d = d < 10 ? ('0' + d) : d
                    this.isAction= action
                    this.isID = index
                    if(this.isAction == 'AddNew'){
                        this.in_time = y + '-' + Mo + '-' + d
                    }else if(this.isAction == 'AddSale'){
                        this.out_time = y + '-' + Mo + '-' + d
                    }else if(this.isAction == 'Change'){
                        let data = this.pdatas[index]
                        this.kind = data.kind
                        this.type_no = data.type_no
                        this.in_price = data.in_price
                        this.in_time = data.in_time
                        this.out_price = data.out_price
                        if(data.out_time){
                            this.out_time = data.out_time
                        }      
                    }
                }else{
                    this.isAction='Nothing'
                    this.isID= -1
                }
            },
            submit_new(){
                let account = get_Session('account')
                let item_list = [this.kind,this.type_no,this.total,this.in_price,this.in_time]
                let isOK = true
                for(var i=0;i<item_list.length;i++){
                    if(!item_list[i]){
                        isOK = false
                        alert('請把資料填完全')
                        break
                    }
                }
                /*新增商品*/
                let data={
                    'kind':this.kind,
                    'type_no':this.type_no,
                    'total':this.total,
                    'in_price':this.in_price,
                    'in_time':this.in_time,
                }
                console.log(this.in_time)
                console.log(typeof(this.in_time))

                if(isOK){
                        padd(JSON.stringify(data),account).then((response)=>{
                        if(response.data.code == 200){
                            alert(response.data.data.message)
                            location.reload()
                        }else{
                            alert('資料上傳失敗,原因:'+ response.data.data.error)
                        }
                    })
                }
            },
            submit_sale(mid){
                let account = get_Session('account')
                /*銷貨*/
                let data = {
                    'mid':mid,
                    'out_price': this.out_price,
                    'out_time':this.out_time
                }
                psale(JSON.stringify(data),account).then((response)=>{
                    if(response.data.code == 200){
                        alert(response.data.data.message)
                        location.reload()
                    }else{
                        alert('商品銷貨失敗,原因:'+ response.data.data.error)
                    }
                })
            },
            submit_change(index){
                let account = get_Session('account')
                /*更改商品資料*/
                let data = this.pdatas[index]
                if(this.kind){
                    data.kind = this.kind
                }                
                if(this.type_no){
                    data.type_no = this.type_no
                }
                if(this.in_price){
                    data.in_price = this.in_price
                }
                if(this.in_time){
                    data.in_time = this.in_time
                }
                if(this.out_price){
                    data.out_price = this.out_price
                }
                if(this.out_time){
                    data.out_time = this.out_time
                }
                padust(data.mid,JSON.stringify(data),account).then((response)=>{
                    if(response.data.code == 200){
                        alert(response.data.data.message)
                        location.reload()
                    }else{
                        alert('資料刪除失敗,原因:'+ response.data.data.error)
                    }

                })

            },
            delete_item(){
                /*刪除商品*/
                let account = get_Session('account')
                if(this.d_list.length){
                    let yes = confirm('你確定刪除選中的項目嗎?');
                    if(yes){
                        let not_ok = false
                        console.log(this.d_list)
                        for(var d=0;d<this.d_list.length;d++){
                            let mid = this.pdatas[this.d_list[d]].mid
                            pdelete(mid,account).then((response)=>{
                                if(response.data.code != 200){
                                    alert('資料刪除失敗,原因:'+ response.data.data.error)
                                    not_ok = true
                                }
                            })
                            if(not_ok){
                                break
                            }
                        }
                        if(!not_ok){
                            alert('刪除已完成')
                            location.reload()
                        }else{
                            alert('請確認刪除項目是否有誤')
                            location.reload()

                        }

                    }
                }else{
                    alert('請勾選欲刪除項目，或是點其他按鈕取消刪除模式')
                }
            }
        },
        async beforeRouteEnter(to,from,next){
          let pattern = get_Session('pattern')
          if(pattern == null){
            pattern = 'all'
            set_Session('pattern',pattern)
          }
          let page = get_Session('page', page)
          if(page == null){
            page = 1
          }
          let browser = get_Session('browser')
          if(browser == null){
            browser = 'summary'
            set_Session('browser',browser)
          }
          let mode = get_Session('mode')
          let keyword = get_Session('keyword')
          let account = get_Session('account')
          if(account ==null){
            account = 'in_database'
            set_Session('account',account)
          }
          await Promise.all([pbrowser(pattern,browser,page,mode,keyword,account),pbrowser('all_money',browser,1,'null','null',account)]).then(([productResponse,productmoneyResponse]) =>{
                next(vm=>{
                    //訂單資料請求
                    if(productResponse.data.code==200){
                        vm.pdatas = productResponse.data.data.list
                        vm.pcounts = productResponse.data.data.pcounts
                    }else{
                        alert(productResponse.data.data.error)
                        del_Session('keyword')
                        del_Session('pattern')
                        del_Session('mode')
                        location.reload()

                    }
                    if(productmoneyResponse.data.code ==200){
                        vm.in_total = productmoneyResponse.data.data.in_total
                        vm.out_total = productmoneyResponse.data.data.out_total                        
                    }
                    if(browser == 'summary'){
                        vm.isAll = true
                    }else{
                        vm.isAll = false
                    }
                    if(account== 'in_database'){
                        vm.isInOut = true
                    }else if(account == 'out_database'){
                        vm.isInOut = false
                    }else{
                        vm.isInOut = true
                    }
                }   
            )
        })
    }
}
</script>
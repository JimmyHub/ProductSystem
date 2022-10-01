<template src='@/assets/templates/users/login.html'></template>
<style scoped src='@/assets/css/common/common.css'></style>
<style scoped src='@/assets/css/users/reg.css'></style>


<script >
    import { login } from '@/api/users.js'
    import { set_session, go_home, search } from '@/assets/js/often.js'
    export default{
        name:'login',
        data(){
            return{
                username:'',
                password:'',
                email:'',
                keyword:'',
                nError:'',
                p1Error:'',
                isCheck:false,
            }
        },
        methods:{
            go_home,search,
            //登入
            submit(){
                //用戶名稱驗證
                if(this.username == ''){
                    this.nError = 'n_empty'
                }else if(this.username.length < 5){
                    this.nError = 'n_form'
                }else{
                    this.nError=''
                }
                //密碼驗證
                if(this.password ==''){
                    this.p1Error = 'p1_empty'
                }else if(this.password.length < 5){
                    this.p1Error = 'p1_form'
                }else{
                    this.p1Error=''
                }
                //確認驗證都沒有問題
                if(this.nError== '' && this.p1Error==''){
                    this.isCheck=true
                }
                //無錯誤情況下才可以發出請求
                if(this.isCheck){
                    let data={
                        'username':this.username,
                        'pwd':this.password,
                        //'pwd':this.password,

                        //'email':this.email,
                    }
                    login(data).then((response)=>{
                        /*if(response.data.key){
                            // set_session('username',response.data.data.username)
                            set_session('token',response.data.key)
                            console.log(document.cookie)
                            if(response.headers){
                                const cookies = response.headers['set-cookie']
                                set_session('cookies',cookies)

                                                    // Axios.defaults.headers.common.Cookie = cookies;
                            }*/
                        if(response.data.code == 200){
                            if(response.data.code){
                                set_session('username',response.data.data.username)
                                set_session('token',response.data.data.token)
                                if(response.headers){
                                    console.log(response.headers)
                                    const cookies = response.headers['Set-Cookie'].join(';');
                                    set_session('cookies',cookies)

                                                        // Axios.defaults.headers.common.Cookie = cookies;
                                }}
                                set_session('loglevel:webpack-dev-server','SILENT')
                                alert(response.data.data.username+'歡迎登入!')
                                window.location.href='#/index'

                        }else{
                            console.log(response)
                            alert(response.data.error+'登入失敗!')
                            location.reload()
                        }
                    })
                }
            },
        }
    }
</script>
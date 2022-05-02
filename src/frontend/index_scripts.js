const { send } = require("express/lib/response")

async function ask() {
    var question = document.getElementById('message-e8bb').value
    if (!question){
        document.getElementsByName('question')[0].placeholder = "Поле не может быть пустым!"
        return false
    }
    window.localStorage['cur_q'] = question
    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.post("/question", {question}).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    window.localStorage['result'] = JSON.stringify(result)
    document.getElementById('message-result').value = "Лучший ответ:\n" + result.answers[0].answer + "\n" + result.answers[0].meta.name + " из " + result.answers[0].meta.law_name

    var old_list = document.getElementById('full_list')
    if (old_list)
        old_list.remove()

    if (!document.getElementById("new_button"))
    {
        var button = document.createElement("button")
        button.setAttribute('type', 'button')
        button.textContent = 'Показать все'
        button.setAttribute('onclick', 'show_others()')
        button.setAttribute('class', "u-btn u-btn-submit u-button-style u-text-hover-grey-90")
        button.setAttribute('style', 'margin-left: -80px')
        var div = document.createElement('div')
        div.appendChild(button)
        div.setAttribute('class', 'u-align-left u-form-group u-form-submit')
        div.setAttribute('id', 'new_button')
        document.getElementById("result_form").appendChild(div)
    }

    if (!document.getElementById("fav_button"))
    {
        var button = document.createElement("button")
        button.setAttribute('type', 'button')
        button.textContent = 'Добавить в избранное'
        button.setAttribute('onclick', 'add_fav()')
        button.setAttribute('class', "u-btn u-btn-submit u-button-style u-text-hover-grey-90")
        button.setAttribute('style', 'margin-top: -70px')
        var div = document.createElement('div')
        div.appendChild(button)
        div.setAttribute('class', 'u-align-left u-form-group u-form-submit')
        div.setAttribute('id', 'fav_button')
        document.getElementById("query_form").appendChild(div)
    }
}

function show_others() {
    var answers = JSON.parse(window.localStorage['result'])
    var base = document.getElementById("result_form")
    var list = document.createElement('ul')
    list.setAttribute('id', 'full_list')
    list.setAttribute('class', 'u-text u-text-1')
    list.setAttribute('style', 'margin-left: -70px; margin-top: 10px; background-color: #FFFFFF; border-radius: 10px; border:1px solid #b3b3b3; white-space: pre-line')
    for (let i = 1; i < answers.answers.length; ++i) {
        var item = document.createElement('li')
        item.textContent = answers.answers[i].answer + "\n" + answers.answers[i].meta.name + " из " + answers.answers[i].meta.law_name
        list.appendChild(item)
    }
    document.getElementById('new_button').remove()
    base.appendChild(list)
}

async function add_fav() {
    if (!window.localStorage['user_id'])
    {
        alert("Необходима авторизация!")
        return false
    }
    var question = document.getElementById('message-e8bb').value
    if (question != window.localStorage['cur_q'])
    {
        return false
    }
    var sending = new Object();
    sending.query = document.getElementById('message-e8bb').value
    sending.answers = JSON.parse(window.localStorage['result']).answers
    sending.user_id = window.localStorage['user_id']
    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.post("/history", sending).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    if (result)
    {
        alert(result)
    }
}

async function register() {
    var login = document.getElementById('username-a30d').value
    var password1 = document.getElementById('password-a30d').value
    var password2 = document.getElementById('password-a30d1').value

    if (password1 != password2)
    {
        alert("Пароли не совпадают")
        return false
    }

    sending = new Object()
    sending.login = login
    sending.password = password1

    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.post("/register", sending).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    if (result)
    {
        alert(result)
        window.location.href = '/login';
    }
}

async function login() {
    var login = document.getElementById('username-a30d').value
    var password = document.getElementById('password-a30d').value

    sending = new Object()
    sending.login = login
    sending.password = password
    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.post("/login", sending).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    if (result)
    {
        window.localStorage['user_id'] = result
        window.location.href = '/';
    }
}

async function get_list()
{
    if (!window.localStorage['user_id'])
    {
        alert("Сначала необходимо войти!")
        window.location.href = '/login'
        return false
    }

    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.get("/history", { params: { user_id: window.localStorage['user_id'] }}).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    var base = document.getElementById("list")
    var list = document.createElement('ul')
    list.setAttribute('id', 'rec_list')
    for (let i = 0; i < result.length; ++i) {
        var item = document.createElement('li')
        item.textContent = result[i].question
        list.appendChild(item)
        var inner_list = document.createElement('ul')
        for (let j = 0; j < result[i].answers.length; ++j) {
            var inner_item = document.createElement('li')
            inner_item.textContent = result[i].answers[j].answer + "\n" + result[i].answers[j].meta.name + " из " + result[i].answers[j].meta.law_name
            inner_list.appendChild(inner_item)
        }
        var button = document.createElement("button")
        button.setAttribute('type', 'button')
        button.textContent = 'Удалить'
        button.setAttribute('id', result[i].id.toString())
        button.setAttribute('onclick', 'delete_question(this.id)')
        button.setAttribute('class', "u-btn u-btn-submit u-button-style u-text-hover-grey-90")

        var div = document.createElement('div')
        div.appendChild(button)
        div.setAttribute('class', 'u-align-left u-form-group u-form-submit')
        list.appendChild(div)
        list.appendChild(inner_list)
    }
    base.appendChild(list)
}

async function delete_question(id) {
    var user_id = window.localStorage['user_id']
    if (!user_id)
    {
        alert("Сначала необходимо войти!")
        window.location.href = '/login';
    }
    sending = new Object()
    sending.user_id = user_id
    sending.question_id = id
    const ms = axios.create({baseURL: "http://localhost:5000"})
    var result = await ms.delete("/history", {data: sending}).then(res=>res.data).catch(function (error) {if (error.response) {alert(error.response.data)}})
    if (result)
    {
        document.getElementById('rec_list').remove()
        get_list()
    }
}

function logout() {
    window.localStorage.removeItem('user_id')
    window.location.href = '/'
}
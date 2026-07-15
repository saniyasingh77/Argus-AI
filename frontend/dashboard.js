function startMonitoring() {

fetch("http://127.0.0.1:5000/start")

.then(res=>res.json())

.then(data=>{

alert(data.message)

})

}



function uploadVideo() {

let file = document.getElementById("file").files[0]

let formData = new FormData()

formData.append("file", file)


fetch("http://127.0.0.1:5000/video", {

method:"POST",

body:formData

})

.then(res=>res.json())

.then(data=>{

alert(data.message)

})

}



function getReport() {

fetch("http://127.0.0.1:5000/report")

.then(res=>res.json())

.then(data=>{

console.log(data)

alert("Report loaded")

})

}



//////////////// ADMIN FUNCTIONS ////////////////



function viewUsers(){

fetch("http://127.0.0.1:5000/get_users")

.then(res=>res.json())

.then(users=>{

if(users.length===0){

alert("No users found")

return

}


let text = "Registered Users:\n\n"


users.forEach(user=>{

text += 
"ID: " + user[0] + "\n" +
"Name: " + user[1] + "\n" +
"Email: " + user[2] + "\n" +
"Role: " + user[3] + "\n" +
"----------------------\n"

})


alert(text)

})

}



function deleteUser(){

let id = prompt("Enter user ID to delete")

if(!id){

alert("Enter valid ID")

return

}


fetch("http://127.0.0.1:5000/delete_user/"+id)

.then(res=>res.json())

.then(data=>{

alert(data.message)

})

}
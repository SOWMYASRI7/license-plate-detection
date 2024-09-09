const express = require('express')
const mongoose = require('mongoose')
const cors=require('cors')
const studentRouter = require('./routes/controller')

//const url = 'mongodb://127.0.0.1:27017/data'
//const url ='mongodb://127.0.0.1:27020,127.0.0.1:27021,127.0.0.1:27022/cbitit1?replicaSet=m101';
const url ='mongodb+srv://sowmyanainala7:<3023777895619>@mern-crud.8uwkr.mongodb.net/?retryWrites=true&w=majority&appName=mern-crud';
const app = express()
mongoose.connect(url)
const con = mongoose.connection


con.on('open', () =>
{
console.log('connected...')
})
app.use(cors())
app.use(express.json())

app.use('/students',studentRouter)
app.listen(9000, () =>
{
console.log('Server started')
})

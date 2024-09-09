const express = require('express')
const router = express.Router()
const Student = require('../models/student')


router.get('/', async(req,res) => 
{
    try
    {
           const students = await Student.find()
           res.json(students)
    }
    catch(err)
    {
        res.send('Error ' + err)
    }
})

router.get('/:id', async(req,res) => 
{
    try
    {
           const student = await Student.findById(req.params.id)
           res.json(student)
    }

catch(err)
{
        res.send('Error ' + err)
    }
})


router.post('/', async(req,res) => 
{
    const student = new Student
   ({
        name: req.body.name,
        tech: req.body.tech,
        sub: req.body.sub,
        rollno: req.body.rollno,
        placement: req.body.placement
    })

    try
   {
        const a1 =  await student.save() 
        res.json(a1)
    }
catch(err)
   {
        res.send('Error')
    }
})

router.patch('/:id',async(req,res)=> 
{
    try
   {
        const student = await Student.findById(req.params.id);
        if (!student) return res.status(404).json({message: 'Student not found'});
        if (req.body.name!=null) student.name=req.body.name;
        if (req.body.tech!=null) student.tech=req.body.tech;
        if (req.body.sub!=null) student.sub=req.body.sub;
        if (req.body.rollno!=null) student.rollno=req.body.rollno;
        if (req.body.placement!=null) student.placement=req.body.placement;

        const s = await student.save();
        res.json(s);
    }
catch(err)
   {
        res.send('Error'+err)
    }

});
//////////////
router.put('/students/:id', async (req, res) => {
    try {
        const student = await Student.findById(req.params.id);
        if (!student) {
            return res.status(404).send('Student not found');
        }
        
        student.name = req.body.name;
        student.tech = req.body.tech;
        student.sub = req.body.sub;
        student.rollno = req.body.rollno;
        student.placement = req.body.placement;

        const a1 = await student.save();
        res.json(a1);
    } catch (err) {
        res.status(400).send('Error: ' + err);
    }
});
//////////
router.delete('/:id', async (req, res) => {
    try {
        const student = await Student.findById(req.params.id);
        if (!student) return res.status(404).json({message: 'Student not found'});
        
        await student.deleteOne();
        res.json({ message: 'Student deleted' });
    } catch (err) {
        res.status(500).send('Error: ' + err.message);
    }
});


module.exports = router;


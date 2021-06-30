console.log("hello world")


const one = document.getElementsByClassName("first")
const two = document.getElementsByClassName("second")
const three = document.getElementsByClassName("third")
const four = document.getElementsByClassName("fourth")
const five = document.getElementsByClassName("fifth")

const form = document.querySelector('.rate-form')

const confirmBox = document.getElementsByClassName('confirm-box')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

const handleSelect = (selection) => {
	switch(selection){
		case 'first':{
			one.classList.add('checked')
			two.classList.remove('checked')
			three.classList.remove('checked')
			four.classList.remove('checked')
			five.classList.remove('checked')
			return

		}
		case 'first':{
			one.classList.add('checked')
			two.classList.add('checked')
			three.classList.remove('checked')
			four.classList.remove('checked')
			five.classList.remove('checked')
			return

		}
		case 'first':{
			one.classList.add('checked')
			two.classList.add('checked')
			three.classList.add('checked')
			four.classList.remove('checked')
			five.classList.remove('checked')
			return

		}
		case 'first':{
			one.classList.add('checked')
			two.classList.add('checked')
			three.classList.add('checked')
			four.classList.add('checked')
			five.classList.remove('checked')
			return

		}
		case 'first':{
			one.classList.add('checked')
			two.classList.add('checked')
			three.classList.add('checked')
			four.classList.add('checked')
			five.classList.add('checked')
			return

		}
	}
}

const arr = [one, two, three, four, five]

arr.forEach(item=> item.addEventListener('mouseover', (event)=>{
	handleSelect(event.target.id)
}))
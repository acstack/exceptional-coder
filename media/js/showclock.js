function displayClock(clk)
	{
	var now=new Date();
	var dateformat=strDay(now.getDay())+" "+strMonth(now.getMonth())+" "+now.getDate()+" "+now.getFullYear();
	var timeformat=now.getHours()+":"+now.getMinutes()+":"+now.getSeconds()
	document.getElementById(clk).innerHTML=dateformat+" "+timeformat;
	setTimeout("displayClock('clk')", 1000)
	}

function strDay(day)
	{
	var days=new Array("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday");
	return days[day];
	}

function strMonth(m)
	{
	var months=new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
	return months[m];
	}

function closeDiv()
	{
	document.getElementById('followers').style.display = 'none';
	document.getElementsByTagName('body')[0].disabled=false;
	}
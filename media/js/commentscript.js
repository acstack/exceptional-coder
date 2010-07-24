function sendAjaxRequest(f,pid)
	{
	var text = document.getElementById('comtext').value;
	if(text == '')
		{
		document.getElementById('err').innerHTML = "<h4> Please write somethng before submitting</h4>";
		document.getElementById('err').style.display = 'block';
		return;
		}
	var xmlhttp = getAjaxRequest();
	xmlhttp.onreadystatechange=function()
		{
		if(xmlhttp.readyState==4)
			{
			if(xmlhttp.status==200)
				{
				//alert(xmlhttp.responseText)
				document.getElementById('coment').innerHTML=xmlhttp.responseText;
				document.getElementById('comtext').value=''
				document.getElementById('err').style.display = 'none';
				}	
			else { alert("some error occured")}
			}
		}
	xmlhttp.open("POST", "/comment/submit/", true);
	xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlhttp.send("comtext="+text+"&pid="+pid);
	}
function getAjaxRequest()
	{
	if(window.XMLHttpRequest)
		{
		xmlhttp = new XMLHttpRequest();
		return xmlhttp;
		}
	else
		{
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		return xmlhttp;
		}
	}
function getFollowers()
	{
	var xmlhttp = getAjaxRequest();
	xmlhttp.onreadystatechange=function()
		{
		if(xmlhttp.readyState==4)
			{
			if(xmlhttp.status==200)
				{
				document.getElementsByTagName('body')[0].disabled=true;
				document.getElementById('followers').innerHTML=xmlhttp.responseText;
				document.getElementById('followers').style.display='block';
				}
			else 
				{ 
				alert("Error getting followers");
				}
			}
		}
	xmlhttp.open("GET", "/buzz/followers/", true)
	xmlhttp.send()
	}
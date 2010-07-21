function sendAjaxRequest(f,pid)
	{
	var text = document.getElementById('comtext').value;
	var xmlhttp = getAjaxRequest();
	xmlhttp.onreadystatechange=function()
		{
		if(xmlhttp.readyState==4)
			{
			if(xmlhttp.status==200)
				{
				//alert(xmlhttp.responseText)
				document.getElementById('coment').innerHTML=xmlhttp.responseText;
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
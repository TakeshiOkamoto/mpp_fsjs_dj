// flashメッセージを削除する
function flash_hide(){
  var obj = document.getElementById("msg_notice");  
  if(obj){
    obj.parentNode.removeChild(obj); 
  }
  
  obj = document.getElementById("msg_alert");  
  if(obj){
    obj.parentNode.removeChild(obj); 
  }
}

// 二重送信対策
function DisableButton(obj){
  obj.disabled = true;
  obj.form.submit();
}
   
// AjaxでDELETEを行う
function ajax_delete(msg, url, jump){
  
  if (confirm(msg)){    
    var xmlhttp = new XMLHttpRequest();

    // イベント
    xmlhttp.onreadystatechange = function() { 
      if (xmlhttp.readyState == 4 && xmlhttp.status == 200) { 
          window.location.href = jump;
      }
    }       
    
    // トークン
    var token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // サーバにHTTPリクエストを送信
    xmlhttp.open("DELETE", url, true);
    xmlhttp.setRequestHeader("Content-Type" , "x-www-form-urlencoded");
    xmlhttp.setRequestHeader("X-CSRFToken", token);  
    xmlhttp.send('');
  }
}

window.addEventListener('load', function(){
  // flashメッセージを3秒後に削除する
  setTimeout(flash_hide, 3000);
});
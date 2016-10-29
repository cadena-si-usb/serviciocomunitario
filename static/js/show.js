var slideIndex = 1;
var cambio = 0

function inicializar() {
  document.getElementById("titulo_proyectos").innerHTML = "Ambientales";
  document.getElementById("desc_proyecto").innerHTML = "Los proyectos ambientales "+ 
  "sirven para crear conciencia sobre el estado del planeta y como podemos hacer para "+
  "renovar los recursos que gastamos irresponsablemente";
  document.getElementById("ambientales").style.background = "#c5c5c5";
  document.getElementById("ambientales").style.color = "white";
}


showDivs(slideIndex);

function plusDivs(n) {
  showDivs(slideIndex += n);
}

function currentDiv(n) {
  showDivs(slideIndex = n);
}

function showDivs(n) {

  if (slideIndex == 0){
    document.getElementById("titulo_proyectos").innerHTML = "Salud";
  document.getElementById("desc_proyecto").innerHTML = "Desde niños hasta adultos y ancianos, "+ 
  "estos proyectos se basan en colaborar con las personas que sufren de alguna enfermedad y que necesitan cualquier tipo de ayuda.";
  document.getElementById("sal").style.background = "#c5c5c5";
  document.getElementById("sal").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  }
  if (slideIndex == 10){
      document.getElementById("titulo_proyectos").innerHTML = "Ambientales";
      document.getElementById("desc_proyecto").innerHTML = "Los proyectos ambientales "+ 
      "sirven para crear conciencia sobre el estado del planeta y como podemos hacer para "+
      "renovar los recursos que gastamos irresponsablemente";
      document.getElementById("ambientales").style.background = "#c5c5c5";
      document.getElementById("ambientales").style.color = "white";
     
      document.getElementById("a_t").style.background = "#fff";
      document.getElementById("a_t").style.color = "black";
      document.getElementById("a_c").style.background = "#fff";
      document.getElementById("a_c").style.color = "black";
      document.getElementById("prev").style.background = "#fff";
      document.getElementById("prev").style.color = "black";
      document.getElementById("cult").style.background = "#fff";
      document.getElementById("cult").style.color = "black";
      document.getElementById("edu").style.background = "#fff";
      document.getElementById("edu").style.color = "black";
      document.getElementById("des").style.background = "#fff";
      document.getElementById("des").style.color = "black";
      document.getElementById("infra").style.background = "#fff";
      document.getElementById("infra").style.color = "black";
      document.getElementById("sal").style.background = "#fff";
      document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 1){
      document.getElementById("titulo_proyectos").innerHTML = "Ambientales";
      document.getElementById("desc_proyecto").innerHTML = "Los proyectos ambientales "+ 
      "sirven para crear conciencia sobre el estado del planeta y como podemos hacer para "+
      "renovar los recursos que gastamos irresponsablemente";
      cambio = 1;
      document.getElementById("ambientales").style.background = "#c5c5c5";
      document.getElementById("ambientales").style.color = "white";
     
      document.getElementById("a_t").style.background = "#fff";
      document.getElementById("a_t").style.color = "black";
      document.getElementById("a_c").style.background = "#fff";
      document.getElementById("a_c").style.color = "black";
      document.getElementById("prev").style.background = "#fff";
      document.getElementById("prev").style.color = "black";
      document.getElementById("cult").style.background = "#fff";
      document.getElementById("cult").style.color = "black";
      document.getElementById("edu").style.background = "#fff";
      document.getElementById("edu").style.color = "black";
      document.getElementById("des").style.background = "#fff";
      document.getElementById("des").style.color = "black";
      document.getElementById("infra").style.background = "#fff";
      document.getElementById("infra").style.color = "black";
      document.getElementById("sal").style.background = "#fff";
      document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 2){
      document.getElementById("titulo_proyectos").innerHTML = "Apoyo Comunitario";
  document.getElementById("titulo_proyectos").style.display = "block";
  
  document.getElementById("desc_proyecto").innerHTML = "Con este tipo de proyectos queremos "+ 
  "atender las distintas necesidades de las comunidades que nos rodean.";
  document.getElementById("a_c").style.background = "#c5c5c5";
  document.getElementById("a_c").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 3){
      document.getElementById("titulo_proyectos").innerHTML = "Apoyo Tecnológico ";
      document.getElementById("desc_proyecto").innerHTML = "A través de los proyectos "+ 
      "de Apoyo Tecnológico pretendemos brindar servicios basados en herramientas computacionales "+
      "para fomentar el aprendizaje en uso de nuevas tecnologías";

      document.getElementById("a_t").style.background = "#c5c5c5";
      document.getElementById("a_t").style.color = "white";



      document.getElementById("ambientales").style.background = "#fff";
      document.getElementById("ambientales").style.color = "black";
      document.getElementById("a_c").style.background = "#fff";
      document.getElementById("a_c").style.color = "black";
      document.getElementById("prev").style.background = "#fff";
      document.getElementById("prev").style.color = "black";
      document.getElementById("cult").style.background = "#fff";
      document.getElementById("cult").style.color = "black";
      document.getElementById("edu").style.background = "#fff";
      document.getElementById("edu").style.color = "black";
      document.getElementById("des").style.background = "#fff";
      document.getElementById("des").style.color = "black";
      document.getElementById("infra").style.background = "#fff";
      document.getElementById("infra").style.color = "black";
      document.getElementById("sal").style.background = "#fff";
      document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 4){
     document.getElementById("titulo_proyectos").innerHTML = "Culturales";
  document.getElementById("desc_proyecto").innerHTML = "Con los proyectos culturales "+ 
  "la idea es rescatar el concepto artístico de las distintas comunidades en Caracas  .";
  document.getElementById("cult").style.background = "#c5c5c5";
  document.getElementById("cult").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";
  }
    if (slideIndex == 5){
    document.getElementById("titulo_proyectos").innerHTML = "Desarrollo Sustentable";
  document.getElementById("desc_proyecto").innerHTML = "Se trata más que nada de saber utilizar "+ 
  "los recursos naturales sabiamente, y en lo posible reutilizarlos.";
  document.getElementById("des").style.background = "#c5c5c5";
  document.getElementById("des").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 6){
      document.getElementById("titulo_proyectos").innerHTML = "Educativos";
    document.getElementById("desc_proyecto").innerHTML = "Mediante los proyectos educativos "+ 
  "brindamos soluciones en las distintas áreas educativas de las escuelas e institutos, desde."+
  "educación básica hasta ciclo diversificado";
  document.getElementById("edu").style.background = "#c5c5c5";
  document.getElementById("edu").style.color = "white";



  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black"
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";;
  }
    if (slideIndex == 7){
      document.getElementById("titulo_proyectos").innerHTML = "Infraestructura";
  document.getElementById("desc_proyecto").innerHTML = "Con este tipo de proyectos buscamos "+ 
  "mantener en lo posible hospitales, parques y escualas en unas condiciones óptimas.";

  document.getElementById("infra").style.background = "#c5c5c5";
  document.getElementById("infra").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 8){
      document.getElementById("titulo_proyectos").innerHTML = "Prevención de emergencias";
    document.getElementById("desc_proyecto").innerHTML = "Los proyectos de prevención "+ 
  "tratan de adiestrar y educar sobre posibles situaciones de riesgo o emergencias que pueden estar presnete en el día a día.";
  document.getElementById("prev").style.background = "#c5c5c5";
  document.getElementById("prev").style.color = "white";



  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  document.getElementById("sal").style.background = "#fff";
  document.getElementById("sal").style.color = "black";
  }
  if (slideIndex == 9){
     document.getElementById("titulo_proyectos").innerHTML = "Salud";
  document.getElementById("desc_proyecto").innerHTML = "Desde niños hasta adultos y ancianos, "+ 
  "estos proyectos se basan en colaborar con las personas que sufren de alguna enfermedad y que necesitan cualquier tipo de ayuda.";
  document.getElementById("sal").style.background = "#c5c5c5";
  document.getElementById("sal").style.color = "white";


  document.getElementById("ambientales").style.background = "#fff";
  document.getElementById("ambientales").style.color = "black";
  document.getElementById("a_t").style.background = "#fff";
  document.getElementById("a_t").style.color = "black";
  document.getElementById("a_c").style.background = "#fff";
  document.getElementById("a_c").style.color = "black";
  document.getElementById("prev").style.background = "#fff";
  document.getElementById("prev").style.color = "black";
  document.getElementById("cult").style.background = "#fff";
  document.getElementById("cult").style.color = "black";
  document.getElementById("edu").style.background = "#fff";
  document.getElementById("edu").style.color = "black";
  document.getElementById("des").style.background = "#fff";
  document.getElementById("des").style.color = "black";
  document.getElementById("infra").style.background = "#fff";
  document.getElementById("infra").style.color = "black";
  }

  var i;
  var x = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("demo");
  if (n > x.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = x.length}
  for (i = 0; i < x.length; i++) {
     x[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
     dots[i].className = dots[i].className.replace(" w3-red", "");
  }
  x[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " w3-red";
}

function ambientales() {

}

function apoyo_tec() {
 


}
function apoyo_com() {
  



}

function cultura() {
 




}

function des_sust() {
  


}
function educa() {





}


function infra() {



}

function prevencion() {



}
function salud() {




}



  
